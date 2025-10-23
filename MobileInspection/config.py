import os

class Config:
    """
    MES系统配置文件
    包含数据库连接配置、应用设置和安全配置
    """
    
    # MySQL数据库配置
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')  # MySQL服务器地址，默认localhost
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))    # MySQL端口，默认3306
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')    # 数据库用户名
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'mm0311')  # 数据库密码
    MYSQL_DB = os.getenv('MYSQL_DB', 'hailan')          # 数据库名称
    
    # 应用配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')  # Flask应用密钥，用于会话加密
    QRCODE_BASE_URL = os.getenv('QRCODE_BASE_URL', 'https://127.0.0.1:5000/cable')  # 二维码链接基础URL
    
    @staticmethod
    def get_mysql_uri():
        """
        生成MySQL连接URI
        返回格式：mysql+pymysql://username:password@host:port/database?charset=utf8mb4
        """
        return f"mysql+pymysql://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DB}?charset=utf8mb4"