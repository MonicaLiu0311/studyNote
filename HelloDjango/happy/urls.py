from django.urls import path, re_path
from django.conf.urls import include

from . import views

app_name = "happy"

urlpatterns = [
    # re_path(r"^login/(?P<year>[0-9]{4})/$", views.login, name="login"),
    path("book/", views.book, name="book"),
    path('add_emp/', views.add_emp, name="add_emp"),

    path('', views.home, name='home'),
    path('login/', views.hlogin, name='login'),
    path('logout/', views.hlogout, name='logout'),
    path('register/', views.hregister, name='register'),
    path('profile/', views.hprofile, name='profile'),
]