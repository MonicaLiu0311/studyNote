"""
vcpkg 仓库自动化管理主程序
功能：
1. 自动分配未分配的Issues和PRs给团队成员
2. 智能分类Issues/PRs并添加标签
3. 验证PR中的vcpkg.json和portfile.cmake文件规范性
4. 自动发送问题提醒

执行流程：
1. 初始化GitHub API连接和任务分配器
2. 扫描所有开放状态的Issues并进行处理
3. 扫描所有开放状态的PRs并进行处理
"""
from core.github_api import GitHubAPI
from core.classifier import Classifier
from core.validator import FileValidator
from core.assigner import Assigner
from config import settings, labels

def main():
    # -------------------- 初始化模块 -------------------- 
    # 创建GitHub API客户端实例（包含自动速率限制）
    gh = GitHubAPI()
    
    # 创建任务分配器实例（基于负载均衡策略）
    assigner = Assigner()
    
    # -------------------- 处理开放Issues -------------------- 
    # 获取所有开放状态的Issue（自动分页处理）
    for issue in gh.get_open_issues():
        # 仅处理未分配的任务（避免重复处理）
        if not issue.assignees:
            # ---------- 智能分类 ----------
            # 调用分类器判断Issue类型（bug/enhancement/question等）
            label_type = Classifier.classify_issue(issue)
            
            # 如果分类成功，添加对应标签
            if label_type:
                gh.add_label(issue, label_type)
                print(f"标记Issue #{issue.number} 为 {label_type}")
            
            # ---------- 任务分配 ----------
            # 获取下一个应分配成员（基于负载均衡算法）
            assignee = assigner.get_next_assignee()
            
            # 实际分配任务（GitHub API操作）
            issue.edit(assignee=assignee)
            print(f"已分配Issue #{issue.number} 给 {assignee}")
    
    # -------------------- 处理开放PRs -------------------- 
    # 获取所有开放状态的PR（自动分页处理）
    for pr in gh.get_open_prs():
        # 仅处理未分配的任务
        if not pr.assignees:
            # ---------- PR分类 ----------
            # 基于文件路径和内容判断PR类型（new-port/port-update/infra等）
            label_type = Classifier.classify_pr(pr)
            
            # 添加分类标签
            if label_type:
                gh.add_label(pr, label_type)
                print(f"标记PR #{pr.number} 为 {label_type}")
            
            # ---------- 文件验证 ----------
            errors = []
            # 检查PR中所有变更文件
            for file in pr.get_files():
                # 验证vcpkg.json文件
                if file.filename.endswith('vcpkg.json'):
                    try:
                        content = file.decoded_content.decode()
                        errors.extend(
                            FileValidator.validate_vcpkg_json(content)
                        )
                    except Exception as e:
                        errors.append(f"vcpkg.json解析失败: {str(e)}")
                
                # 验证portfile.cmake文件
                elif file.filename.endswith('portfile.cmake'):
                    try:
                        content = file.decoded_content.decode()
                        errors.extend(
                            FileValidator.validate_portfile(content)
                        )
                    except Exception as e:
                        errors.append(f"portfile.cmake解析失败: {str(e)}")
            
            # ---------- 问题反馈 ----------
            # 如果发现验证错误，在PR中创建评论提醒
            if errors:
                error_msg = "⚠️ vcpkg 文件规范检查发现问题:\n" + "\n".join(f"- {e}" for e in errors)
                pr.create_issue_comment(error_msg)
                print(f"在PR #{pr.number} 中发现 {len(errors)} 个问题")
            
            # ---------- 任务分配 ----------
            # 分配PR给团队成员
            assignee = assigner.get_next_assignee()
            pr.edit(assignee=assignee)
            print(f"已分配PR #{pr.number} 给 {assignee}")

if __name__ == "__main__":
    # 安全执行主程序（捕获并记录异常）
    try:
        print("=== vcpkg 自动化管理开始运行 ===")
        main()
        print("=== 任务执行完成 ===")
    except Exception as e:
        print(f"!!! 运行时错误: {str(e)}")
        raise