from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
import time, inspect

# 登录状态检查中间件
class AuthCheckMiddleware(MiddlewareMixin):
    def process_request(self, request):
        print(f"---3---{self.__class__.__name__} {inspect.currentframe().f_code.co_name} 执行")
        # 允许未登录访问的路径
        allow_paths = [
            '/happy/login',
            '/happy/register',
            '/captcha/',
            '/static/',
            # '/favicon.ico', # 浏览器自动请求 favicon.ico
            # '/.well-known/',  # 添加 Chrome 开发工具路径
            # '/robots.txt' 
        ]

        if any(request.path.startswith(p) for p in allow_paths):
            return None

        # 检查 Session 中的登录状态，使用自定义的 request.session['is_login']
        if not request.session.get("is_login"):
            messages.error(request, "请先登录！")
            return HttpResponseRedirect(f"{reverse('happy:login')}?next={request.path}")
    
    def process_response(self, request, response):
        print(f"---3---{self.__class__.__name__} {inspect.currentframe().f_code.co_name} 执行")
        # 自定义属性标记​​，用于防止中间件的 process_response 被重复执行，
        # ​​临时属性​​：仅存在于当前请求生命周期，响应后销毁
        if not hasattr(request, '_auth_middleware_processed'): 
            # 添加安全响应头
            response['X-Content-Type-Options'] = 'nosniff'
            request._auth_middleware_processed = True
        return response

# 请求日志中间件
class LoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):  # 新增方法
        request.start_time = time.time()  # 统一初始化时间戳

    def process_view(self, request, view_func, view_args, view_kwargs):
        print(f"---2---{self.__class__.__name__} {inspect.currentframe().f_code.co_name} 执行")
        # 记录请求信息，传递请求时间，适配自定义 request.session['user1']
        print(f"[{time.ctime()}] 访问 {view_func.__name__} | 用户 {request.session.get('user1', '匿名')}")
    
    def process_response(self, request, response):
        print(f"---2---{self.__class__.__name__} {inspect.currentframe().f_code.co_name} 执行")
        # 记录响应耗时
        duration = time.time() - request.start_time
        print(f"[{time.ctime()}] 响应 {request.path} | 状态 {response.status_code} | 耗时 {duration:2f}s")
        return response

# 统一异常处理中间件
class ErrorHandlerMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        print(f"---1---{self.__class__.__name__} {inspect.currentframe().f_code.co_name} 执行")
        # 记录错误日志
        print(f"[ERROR] {time.ctime()} {request.path} 出现了错误： {str(Exception)}")

        # 返回友好错误页
        if request.path.startswith("/happy/"):
            return HttpResponse("服务器开小差了，请稍后再试！", status=500)
        
        # 其他路径的异常交给 Django 默认处理
        return None