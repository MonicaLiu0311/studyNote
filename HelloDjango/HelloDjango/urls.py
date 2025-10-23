"""
URL configuration for HelloDjango project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from . import search, search_post, views, testdb

urlpatterns = [
    path('admin/', admin.site.urls),
    path('captcha/', include('captcha.urls')),  # 验证码URL
    path('hello/', views.hello, name='hello'),
    path('testdb/', testdb.testdb, name='testdb'),
    path('search_form/', search.search_form, name='search_form'),
    path('search/', search.search, name='search'),
    path('search_post/', search_post.search_post, name='search_post'),
    path('happy/', include('happy.urls', namespace='happy')),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# 通用静态资源处理（开发+生产环境）
def serve_static(prefix, root):
    # 动态生成 Django 静态资源的路由规则
    # path(route, view,kwargs=None)  Django 的路由定义函数 
    # route: URL模式 (如 'static/<path:path>'), view: 视图函数, kwargs: 传递给视图的额外参数
    # prefix：URL 前缀（如 /static/、/media/）
    # root：服务器上对应的物理路径（如 /var/www/static/）
    # <path:path>: 匹配 URL 中 prefix后的所有内容。例如： 请求 /static/js/app.js → 捕获 path='js/app.js'
    # serve视图​​： Django 内置的静态文件处理视图，根据 document_root 和捕获的 path 返回文件内容
    # 例如： 访问 http://yoursite.com/static/css/style.css → 返回 /var/www/static/css/style.css文件内容
    return [
        path(f'{prefix}<path:path>', serve, {'document_root': root})
    ]

# 静态文件（CSS/JS）
urlpatterns += serve_static(settings.STATIC_URL, settings.STATIC_ROOT)

# 媒体文件（用户上传）
urlpatterns += serve_static(settings.MEDIA_URL, settings.MEDIA_ROOT)

# 特殊路径（如验证码、favicon等）
urlpatterns += [
    path('.well-known/<path:path>', serve, {'document_root': '/var/www/.well-known'}),
    path('favicon.ico', serve, {'document_root': settings.STATIC_ROOT, 'path': 'img/favicon.ico'}),
]