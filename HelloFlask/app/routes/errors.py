# errors.py: 自定义错误处理功能

from flask import render_template
from app import db

# 集中注册所有错误处理器，渲染自定义的错误页面模板
def register_error_handlers(app):
    # @app.errorhandler(error_code) 是 Flask 中用于自定义处理错误的装饰器，必须返回响应内容和状态码
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_error(error):
        # 回滚数据库会话，防止部分失败的数据库操作导致数据不一致
        db.session.rollback()
        return render_template('errors/500.html'), 500