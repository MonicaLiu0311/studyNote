"""
GitHub API 和项目配置常量
"""
import os

class Config:
    # GitHub 认证
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # 从环境变量读取
    REPO_NAME = "microsoft/vcpkg"
    
    # 团队成员
    TEAM_MEMBERS = [
        "user1", "user2", "user3", 
        "user4", "user5", "user6", "user7"
    ]
    
    # API 速率限制控制
    API_CALLS_PER_HOUR = 5000
    REQUEST_DELAY = 1  # 秒