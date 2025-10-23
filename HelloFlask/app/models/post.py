# post.py: Post模型类，用于表示博客中的文章

from datetime import datetime, timezone
from app import db
# ​​导入模块​​：
# datetime: 用于处理时间相关的功能
# db: SQLAlchemy 数据库实例（从主应用导入）

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    body = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # ​​__repr__​​: 对象的字符串表示形式，用于调试和日志记录，示例输出: <Post My First Blog Post>
    def __repr__(self):
        return f'<Post {self.title}>'