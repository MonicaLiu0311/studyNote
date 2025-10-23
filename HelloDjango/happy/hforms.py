from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from captcha.fields import CaptchaField
import re

from . import models
    
class LoginForm(forms.Form):
    username = forms.CharField(label="用户名")
    password = forms.CharField(label="密码", widget=forms.PasswordInput())
    captcha = CaptchaField(label="验证码")

class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label="用户名",
        max_length=150,
        help_text="必填。150个字符以内，只能包含字母、数字和@/./+/-/_。",
        error_messages={
            'required': '用户名不能为空',
            'max_length': '用户名不能超过150个字符'
        }
    )
    
    email = forms.EmailField(
        label="邮箱", 
        required=True,
        help_text="请输入有效的邮箱地址",
        error_messages={
            'required': '邮箱不能为空',
            'invalid': '请输入有效的邮箱地址'
        }
    )
    
    password1 = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(),
        help_text="密码必须包含大写字母、小写字母、数字和特殊字符，且不少于8位",
        error_messages={
            'required': '密码不能为空'
        }
    )
    
    password2 = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput(),
        help_text="请再次输入相同的密码以确认",
        error_messages={
            'required': '请确认密码'
        }
    )
    
    captcha = CaptchaField(label="验证码")

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")

        if len(password1) < 8:
            raise forms.ValidationError("密码长度不能少于8位")
        
        if not re.search(r'[A-Z]', password1):
            raise forms.ValidationError("密码必须包含至少一个大写字母")
            
        if not re.search(r'[a-z]', password1):
            raise forms.ValidationError("密码必须包含至少一个小写字母")
            
        if not re.search(r'[0-9]', password1):
            raise forms.ValidationError("密码必须包含至少一个数字")
            
        if not re.search(r'[^A-Za-z0-9]', password1):
            raise forms.ValidationError("密码必须包含至少一个特殊字符")
            
        return password1
    

class EmpForm(forms.Form):
    name = forms.CharField(min_length=5, label="姓名", error_messages={"required": "该字段不能为空!",
                                                                     "min_length": "用户名太短。"})
    age = forms.IntegerField(label="年龄")
    salary = forms.DecimalField(max_digits=8, decimal_places=2, label="工资")
    r_salary = forms.DecimalField(max_digits=8, decimal_places=2, label="请再输入工资")


    def clean_name(self):  # 局部钩子
        val = self.cleaned_data.get("name")


        if val.isdigit():
            raise ValidationError("用户名不能是纯数字")
        elif models.Emp.objects.filter(name=val):
            raise ValidationError("用户名已存在！")
        else:
            return val

    def clean(self):  # 全局钩子 确认两次输入的工资是否一致。
        val = self.cleaned_data.get("salary")
        r_val = self.cleaned_data.get("r_salary")


        if val == r_val:
            return self.cleaned_data
        else:
            raise ValidationError("请确认工资是否一致。")