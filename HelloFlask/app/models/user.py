# models/user.py: User 模型类，用于处理用户认证和数据库交互

from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
# ​​导入模块​​：
# db: SQLAlchemy 数据库实例
# login: Flask-Login 的 LoginManager 实例
# generate_password_hash/check_password_hash: Werkzeug 的安全工具
# UserMixin: Flask-Login 的用户基类

# UserMixin: 提供 Flask-Login 需要的默认方法（如 is_authenticated 等）
# db.Model: SQLAlchemy 的模型基类
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    # db.relationship: 一对多关系
    # backref='author': 在 Post 模型中可以通过 author 访问用户
    # lazy='dynamic': 返回可额外过滤的查询对象
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    # 使用 PBKDF2-HMAC-SHA256 算法（Werkzeug 默认）
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# 用户加载器：根据会话中存储的用户ID获取用户对象
@login.user_loader
def load_user(id):
    return User.query.get(int(id))