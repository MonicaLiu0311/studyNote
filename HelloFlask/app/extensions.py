# extensions.py: 自定义扩展功能模块 

class SimpleExtension:
    # ​​双初始化模式​​：
    # 支持直接初始化：SimpleExtension(app)
    # 支持延迟初始化：ext = SimpleExtension() + ext.init_app(app)

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    # ​​扩展注册​​：将扩展实例存储在 app.extensions 字典中，使用唯一键名 'simple_extension' 避免冲突
    # 他代码可以通过 current_app.extensions['simple_extension'] 访问扩展
    def init_app(self, app):
        app.extensions['simple_extension'] = self
        
        # 请求钩子注册
        # ​​before_request​​：在每个请求处理前执行
        # 这里只是记录日志
        @app.before_request
        def before_request():
            app.logger.info('Before request - SimpleExtension')
        
        # after_request​​：在每个请求处理后执行，必须接收并返回 response 对象
        # 记录日志后返回原始响应
        @app.after_request
        def after_request(response):
            app.logger.info('After request - SimpleExtension')
            return response

# ​​单例模式​​：创建全局可用的扩展实例，便于在多个模块中导入使用
simple_extension = SimpleExtension()