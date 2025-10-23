from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from config import Config

# 创建扩展对象
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
mail = Mail()

# 工厂函数：封装应用创建逻辑，创建和配置应用实例
# config_class: 默认为 Config类，可以传入不同的配置类
def create_app(config_class=Config):
    # 创建 Flask 实例对象
    app = Flask(__name__)

    # 从 config.py 中的 Config 类加载配置，后续可以通过实例 app.config 来调用
    app.config.from_object(config_class)

    # 将之前创建的扩展对象绑定到应用实例
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)

    # 导入 routes 模块，​​将蓝图注册到 Flask 应用实例​中，为每个蓝图指定 URL 前缀
    from app.routes.auth import auth_bp
    from app.routes.blog import blog_bp
    from app.routes.user import user_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(blog_bp, url_prefix='/blog')
    app.register_blueprint(user_bp, url_prefix='/user')

    # 注册自定义开发的 Flask 扩展并初始化
    from app.extensions import simple_extension
    simple_extension.init_app(app)

    # 注册错误处理器，集中处理HTTP错误
    from app.routes.errors import register_error_handlers
    register_error_handlers(app)

    return app

# 导入模型（用于数据库迁移）
from app.models import user, post
