"""
Issue/PR 智能分类器
功能：基于内容和文件路径自动分类GitHub Issues和Pull Requests
设计目标：通过多级判断实现高准确率的自动化分类
"""

import re
from typing import Optional

class Classifier:
    @staticmethod
    def classify_issue(issue) -> Optional[str]:
        """
        Issue分类逻辑（基于文本内容分析）
        
        参数：
            issue : GitHub.Issue.Issue
                GitHub Issue对象，需包含title和body属性
        
        返回：
            Optional[str]: 
                返回分类标识字符串，无法分类时返回None
                可能值: 'bug'|'enhancement'|'question'
        
        算法逻辑：
            1. 合并标题和正文内容为统一文本
            2. 转换为小写消除大小写干扰
            3. 关键词匹配确定分类优先级：
               bug > enhancement > question
            4. 无匹配关键词时返回None
        """
        # 合并标题和正文（处理可能的None值）
        content = f"{issue.title} {issue.body or ''}".lower()
        
        # 优先级1：缺陷报告检测
        # 匹配关键词：bug/error/fail等（可根据项目需求扩展）
        if any(kw in content for kw in ['bug', 'error', 'fail', 'crash', 'broken']):
            return 'bug'
        
        # 优先级2：功能增强检测
        # 匹配关键词：feat/enhance/improve等
        elif any(kw in content for kw in ['feat', 'enhance', 'improve', 'optimize']):
            return 'enhancement'
        
        # 优先级3：问题咨询检测
        # 简单通过问号识别（可结合NLP增强）
        elif '?' in content:
            return 'question'
        
        # 未匹配任何分类
        return None

    @staticmethod
    def classify_pr(pr) -> Optional[str]:
        """
        PR分类逻辑（基于文件路径和标题分析）
        
        参数：
            pr : GitHub.PullRequest.PullRequest
                GitHub PR对象，需包含get_files()方法和title属性
        
        返回：
            Optional[str]:
                返回分类标识字符串，无法分类时返回None
                可能值: 'new-port'|'port-update'|'infra'
        
        算法逻辑：
            1. 检查是否修改ports/目录 → 端口相关PR
                - 根据标题是否含"new port"区分新增/更新
            2. 检查是否修改.github/目录 → 基础设施变更
            3. 其他情况返回None
        """
        files = pr.get_files()  # 获取PR修改的文件列表
        
        # ---------- 端口变更检测 ----------
        # 匹配ports/目录下的文件变更
        port_files = [f for f in files if 'ports/' in f.filename]
        if port_files:
            # 通过标题判断是新增端口还是更新现有端口
            return 'new-port' if 'new port' in pr.title.lower() else 'port-update'
        
        # ---------- 基础设施变更检测 ----------
        # 匹配CI/CD或仓库配置变更
        infra_paths = ['.github/', 'scripts/', 'cmake/']
        if any(
            f.filename.startswith(path) 
            for f in files 
            for path in infra_paths
        ):
            return 'infra'
        
        # ---------- 其他情况 ----------
        return None

    @staticmethod
    def _is_security_issue(content: str) -> bool:
        """
        安全漏洞问题检测（辅助方法）
        
        参数：
            content : str
                合并后的issue内容文本
        
        返回：
            bool:
                是否包含安全相关关键词
        
        设计说明：
            可作为classify_issue的扩展点，需根据项目需求定制关键词
        """
        security_keywords = [
            'security', 'vulnerability', 'cve', 
            'xss', 'injection', 'privilege'
        ]
        return any(
            re.search(rf'\b{kw}\b', content, re.IGNORECASE) 
            for kw in security_keywords
        )