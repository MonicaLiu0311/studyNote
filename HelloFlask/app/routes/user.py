# routes/user.py: 用户资料页，显示用户信息和其发布的文章列表

from flask import Blueprint, render_template, abort
from flask_login import current_user, login_required
from sqlalchemy import text
from app.models.user import User
# ​​导入模块​​：
# Blueprint: 创建模块化路由
# render_template: 渲染模板
# abort: 触发HTTP错误
# current_user/login_required: Flask-Login 功能
# User: 用户模型

# 创建名为 'user' 的蓝图，所有路由 URL 将以 /user 为前缀（在应用工厂中设置）
user_bp = Blueprint('user', __name__)

@user_bp.route('/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(text('timestamp desc')).limit(10)
    return render_template('user/profile.html', user=user,posts=posts)