import os
from datetime import datetime

class Config:
    """
    应用程序配置类
    包含数据库连接信息和国网平台API配置
    """
    
    # MySQL数据库配置
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'mm0311')
    MYSQL_DB = os.getenv('MYSQL_DB', 'hailan')
    
    # 国网平台API配置
    GRID_API_BASE_URL = os.getenv('GRID_API_BASE_URL', 'https://127.0.0.1:5000/grid')
    GRID_API_CLIENT_ID = os.getenv('GRID_API_CLIENT_ID', 'test_client_001')
    GRID_API_CLIENT_SECRET = os.getenv('GRID_API_CLIENT_SECRET', 'test_secret_123')
    GRID_API_TOKEN_URL = os.getenv('GRID_API_TOKEN_URL', '/oauth/token')
    GRID_API_DATA_URL = os.getenv('GRID_API_DATA_URL', '/api/v1/data/upload')
    
    # 应用配置
    DEFAULT_DATA_LIMIT = int(os.getenv('DEFAULT_DATA_LIMIT', 100))  # 默认数据条数
    MAX_DATA_LIMIT = int(os.getenv('MAX_DATA_LIMIT', 1000))       # 最大数据条数
    
    @staticmethod
    def get_mysql_uri():
        """
        构建MySQL数据库连接URI
        返回格式: mysql+pymysql://username:password@host:port/database
        """
        return f"mysql+pymysql://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DB}?charset=utf8mb4"
    
    @staticmethod
    def get_grid_api_url(endpoint):
        """
        构建国网平台API完整URL
        """
        return f"{Config.GRID_API_BASE_URL}{endpoint}"