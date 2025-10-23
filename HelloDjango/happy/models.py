from django.db import models as m
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# 书籍表 Book：title 、 price 、 pub_date 、 publish（外键，多对一） 、 authors（多对多）
# 出版社表 Publish：name 、 city 、 email
# 作者表 Author：name 、 age 、 au_detail（一对一）
# 作者详情表 AuthorDetail：gender 、 tel 、 addr 、 birthday

# Create your models here.
class Book(m.Model):
    title = m.CharField(max_length=64)
    price = m.DecimalField(max_digits=5, decimal_places=2)
    pub_date = m.DateField()
    publish = m.ForeignKey("Publish", on_delete=m.CASCADE)
    author = m.ManyToManyField("Author")

class Publish(m.Model):
    name = m.CharField(max_length=32)
    city = m.CharField(max_length=64)
    email = m.EmailField()

class Author(m.Model):
    name = m.CharField(max_length=32)
    age = m.SmallIntegerField()
    au_detail = m.OneToOneField("AuthorDetail", on_delete=m.CASCADE)

class AuthorDetail(m.Model):
    gender_choices = ((0, "女"), (1, "男"), (2,"保密"))
    gender = m.SmallIntegerField(choices=gender_choices)
    tel = m.CharField(max_length=32)
    addr = m.CharField(max_length=64)
    birthday = m.DateField()

class Emp(m.Model): 
    name = m.CharField(max_length=32) 
    age = m.IntegerField()
    salary = m.DecimalField(max_digits=8, decimal_places=2)
    dep = m.CharField(max_length=32) 
    province = m.CharField(max_length=32)

class Emps(m.Model): 
    name = m.CharField(max_length=32) 
    age = m.IntegerField() 
    salary = m.DecimalField(max_digits=8, decimal_places=2) 
    dep = m.ForeignKey("Dep", on_delete=m.CASCADE)
    province = m.CharField(max_length=32) 
    
class Dep(m.Model): 
    title = m.CharField(max_length=32)