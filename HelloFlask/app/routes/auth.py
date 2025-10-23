# auth.py: 完整的用户认证系统，包含登录、注销和注册功能

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.models.user import User
from app import db
from urllib.parse import urlparse
# ​​导入模块​​：
# Blueprint: 创建模块化路由
# render_template: 渲染模板
# redirect/url_for: 重定向和URL生成
# flash: 显示用户消息
# request: 访问请求数据
# login_user/logout_user/current_user: Flask-Login 功能
# User: 用户模型
# db: SQLAlchemy 数据库实例
# url_parse: 解析 URL 确保安全

# 创建名为 'auth' 的蓝图，所有路由将以 /auth 为前缀（在工厂函数中设置）
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # 已登录用户直接跳转到博客首页
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))
    
    # POST 请求：处理登录表单提交
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        # check_password: 验证哈希密码（在User模型中实现）
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        
        # 建立用户会话，标记用户为已登录状态
        login_user(user)
        next_page = request.args.get('next')
        # urlparse(next_page).netloc: 解析 next_page 的 URL，检查是否包含​域名（netloc），防止开放重定向攻击
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('blog.index')
        return redirect(next_page)
    
    # GET 请求：显示登录表单
    return render_template('auth/login.html', title='Sign In')

@auth_bp.route('/logout')
def logout():
    # 终止用户会话
    logout_user()
    return redirect(url_for('blog.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # 已登录用户直接跳转到博客首页
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))
    
    # POST 请求：处理注册表单提交
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('auth.register'))
        
        # 创建新用户并设置密码（自动哈希）
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    
    # GET 请求：显示注册表单
    return render_template('auth/register.html', title='Register')