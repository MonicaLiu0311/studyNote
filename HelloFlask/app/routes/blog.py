# blog.py: 完整的博客系统，处理博客文章的创建、编辑、删除和显示

from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import current_user, login_required
from app.models.post import Post
from app.models.user import User
from app import db
from datetime import datetime
# ​​导入模块​​：
# Blueprint: 创建模块化路由
# render_template: 渲染模板
# request: 访问请求数据
# flash: 显示用户消息
# redirect/url_for: 重定向和URL生成
# abort: 触发HTTP错误
# current_user/login_required: Flask-Login 功能
# Post: 文章模型
# User: 用户模型

# 创建名为 'blog' 的蓝图，所有路由 URL 将以 /blog 为前缀（在应用工厂中设置）
blog_bp = Blueprint('blog', __name__)

# 显示分页的文章列表，按时间倒序排列，每页显示5篇文章
@blog_bp.route('/')
def index():
    # 获取当前页码，默认值为1
    page = request.args.get('page', 1, type=int) 
    # paginate()方法实现分页功能，error_out=False: 页码超出范围不返回 404，而是返回最后一页
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page,
        per_page=5,
        error_out=False
    )
    return render_template('blog/index.html', posts=posts)

# 创建文章，@login_required 装饰器确保只有登录用户可访问
@blog_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    # POST: 处理表单提交，创建新文章
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        
        if not title or not body:
            flash('Title and body are required')
            return redirect(url_for('blog.create'))
        
        post = Post(title=title, body=body, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!')
        return redirect(url_for('blog.index'))
    
    # GET: 显示创建表单
    return render_template('blog/create.html')

# 文章详情页
@blog_bp.route('/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('blog/post.html', post=post)

# 编辑文章，只有文章作者可编辑
@blog_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    # 确保文章存在（get_or_404），检查当前用户是否是文章作者（否则返回403禁止访问）
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    
    # POST: 更新文章内容
    if request.method == 'POST':
        post.title = request.form['title']
        post.body = request.form['body']
        db.session.commit()
        flash('Your post has been updated!')
        return redirect(url_for('blog.post', post_id=post.id))
    
    # GET: 显示编辑表单（预填充当前内容）
    return render_template('blog/edit.html', post=post)

# 删除文章，只有文章作者可删除
@blog_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):
    # 确保文章存在（get_or_404），检查当前用户是否是文章作者（否则返回403禁止访问）
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!')
    return redirect(url_for('blog.index'))