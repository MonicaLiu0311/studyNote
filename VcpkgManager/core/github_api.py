"""
GitHub API 交互封装类
功能：提供安全、高效的GitHub API调用接口，包含速率限制控制和常用操作封装
设计目标：降低API调用复杂度，防止触发速率限制，统一错误处理
"""

from github import Github, GithubException  # PyGithub库
from config.settings import Config
from config.labels import LABEL_DEFINITIONS
import time  # 用于速率控制

class GitHubAPI:
    def __init__(self):
        """
        初始化GitHub API客户端
        
        属性：
        - gh : Github
            PyGithub客户端实例
        - repo : Repository
            目标仓库对象（microsoft/vcpkg）
        - last_request_time : float
            最后一次API调用时间戳（用于速率控制）
        """
        # 使用配置中的Token初始化GitHub客户端
        self.gh = Github(Config.GITHUB_TOKEN)
        
        # 获取目标仓库对象（自动验证仓库是否存在）
        self.repo = self.gh.get_repo(Config.REPO_NAME)
        
        # 初始化速率控制计时器
        self.last_request_time = 0  # 0表示尚未发起过请求

    def _rate_limit(self):
        """
        内部速率限制控制方法
        
        实现逻辑：
        1. 计算距上次请求的时间间隔
        2. 如果间隔小于配置的延迟时间，休眠剩余时间
        3. 更新最后一次请求时间戳
        
        注意：
        - GitHub API限制为5000请求/小时（认证用户）
        - 默认配置REQUEST_DELAY=1秒可保持安全调用频率
        """
        elapsed = time.time() - self.last_request_time
        if elapsed < Config.REQUEST_DELAY:
            # 计算需要休眠的时间（毫秒级精度）
            sleep_time = Config.REQUEST_DELAY - elapsed
            time.sleep(sleep_time)
        
        # 更新请求时间戳（以方法结束时间为准）
        self.last_request_time = time.time()

    def get_open_issues(self):
        """
        获取仓库所有开放状态的Issue
        
        返回：
            PaginatedList[Issue]: 
                GitHub Issue对象的可迭代列表（自动分页）
        
        速率控制：
            - 每次调用自动触发_rate_limit检查
            - 实际API调用：GET /repos/{owner}/{repo}/issues?state=open
        """
        self._rate_limit()  # 前置速率检查
        return self.repo.get_issues(state='open')  # state参数过滤开放状态的issue

    def get_open_prs(self):
        """
        获取仓库所有开放状态的Pull Request
        
        返回：
            PaginatedList[PullRequest]: 
                GitHub PR对象的可迭代列表（自动分页）
        
        注意：
            - 与get_open_issues()的区别：专门获取PR而非Issue
            - PR在GitHub API中实际是特殊的Issue类型
        """
        self._rate_limit()
        return self.repo.get_pulls(state='open')  # state参数过滤开放状态的PR

    def add_label(self, item, label_type):
        """
        为Issue/PR添加预定义标签
        
        参数：
            item : Union[Issue, PullRequest]
                GitHub的Issue或PR对象
            label_type : str
                预定义的标签类型（参考config/labels.py）
        
        逻辑：
            1. 根据item类型（Issue/PR）选择对应的标签定义
            2. 检查标签是否已存在
            3. 添加标签到目标item
        
        异常：
            - GithubException: 标签不存在或API调用失败
            - KeyError: 无效的label_type
        """
        self._rate_limit()
        
        # 判断item类型（PR或Issue）以选择正确的标签定义
        is_pr = hasattr(item, 'merge_commit_sha')  # PR特有属性
        label_category = 'prs' if is_pr else 'issues'
        
        try:
            # 从配置获取标签定义（可能触发KeyError）
            label_name = LABEL_DEFINITIONS[label_category][label_type]['name']
            
            # 检查标签是否已存在（防止重复添加）
            existing_labels = {label.name for label in item.get_labels()}
            if label_name not in existing_labels:
                item.add_to_labels(label_name)
        except GithubException as e:
            print(f"添加标签失败: {e.data.get('message', '未知错误')}")
            raise
        except KeyError:
            print(f"无效标签类型: {label_type} (可用类型: {list(LABEL_DEFINITIONS[label_category].keys())})")
            raise

    def create_issue_comment(self, issue_or_pr, body):
        """
        在Issue/PR下创建评论
        
        参数：
            issue_or_pr : Union[Issue, PullRequest]
                目标Issue或PR对象
            body : str
                评论内容（Markdown格式）
        """
        self._rate_limit()
        issue_or_pr.create_comment(body)

    def close_issue(self, issue):
        """
        关闭Issue
        
        参数：
            issue : Issue
                要关闭的Issue对象
        
        注意：
            - 对PR无效（需使用merge_pull_request）
        """
        self._rate_limit()
        issue.edit(state='closed')