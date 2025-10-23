# config.py: Flask 应用程序的配置类，用于集中管理应用程序的各种设置
# 通常会在 Flask 应用初始化时加载这些配置，例如： app.config.from_object(Config)

import os

# from dotenv import load_dotenv
# load_dotenv()  # 加载 .env 文件中的环境变量

class Config:
    # SECRET_KEY: 用于加密会话(cookies)和其他安全相关的功能，优先从环境变量 SECRET_KEY 获取，若无则使用默认值
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # ​​SQLALCHEMY_DATABASE_URI​​: 数据库连接字符串
    # 格式: dialect+driver://username:password@host:port/database
    # 这里使用的是 MySQL 数据库，通过 PyMySQL 驱动连接，连接的是本地的 'flask_demo' 数据库
    # SQLALCHEMY_TRACK_MODIFICATIONS​​: SQLAlchemy 的追踪修改功能
    # 设置为 False 以避免带来的额外内存开销，除非需要 Flask-SQLAlchemy 的事件系统，否则建议保持 False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:mm0311@localhost/harlen'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ​​MAIL_SERVER​​: SMTP 服务器地址
    # ​​MAIL_PORT​​: SMTP 服务器端口 (587 是 TLS 的标准端口)
    # ​​MAIL_USE_TLS​​: 启用 TLS 加密
    # ​​MAIL_USERNAME​​ 和 ​​MAIL_PASSWORD​​: 从环境变量获取邮件服务器的登录凭证，这种做法比硬编码在代码中更安全
    # MAIL_SERVER = '1247503628@qq.com'
    # MAIL_PORT = 465
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SERVER = 'smtp.163.com'  # 163邮箱SMTP服务器地址
    MAIL_PORT = 465  # SSL加密端口
    MAIL_USE_SSL = True  # 163邮箱要求使用SSL加密
    MAIL_USERNAME = 'qiaoxia916@163.com'  # 你的163邮箱地址
    MAIL_PASSWORD = 'DSjT636ngBx8GUyN'  # SMTP授权码（不是邮箱密码）
    MAIL_DEFAULT_SENDER = 'MonicaLiu@163.com'  # 默认发件人