from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.forms.models import model_to_dict
from django.db.models import Avg,Max,Min,Count,Sum,F,Q
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from . import models, hforms

# Create your views here.
# def login(request, year):
#     if request.method == 'POST':
#         user = request.POST.get("user")
#         pwd = request.POST.get("pwd")

#         if user == "monica" and pwd == "monica":
#             return HttpResponse(f"恭喜你登录了 happy 页面！ {year} 年")
#             # result = f"恭喜你登录了 happy 页面！ {year} 年"
#             # return render(request, "home.html", {"result": result})
#         else:
#             return redirect(reverse("happy:login", kwargs={'year': year}))
#     else:
#         return render(request, 'login.html', {'year': year})

# 首页
def home(request):
    # status = request.COOKIES.get('is_login') # 收到浏览器的再次请求,判断携带的cookie是不是登录成功响应的 cookie
    status = dict(request.session.items())
    print(f"------home------session:{status}")
    if not status:
        return redirect('/login/')
    return render(request, "home.html")

# 登录
def hlogin(request):
    if request.method == "POST":
        form = hforms.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                # 获取 next 参数，如果不存在跳转到首页
                next_url = request.GET.get("next") or reverse("happy:home")
                # rep = redirect(next_url)
                # rep.set_cookie("is_login", True) # 设置 cookie
                # return rep
                request.session['is_login'] = True
                request.session['user1'] = username
                return redirect(next_url)
            else:
                messages.error(request, "用户名或者密码错误。")

    else:
        form = hforms.LoginForm()
        
    # GET 或者 请求失败返回登录页面
    return render(request, "login.html", {"form": form})

# 登出
def hlogout(request):
    logout(request)
    # rep = redirect("happy:login")
    # rep.delete_cookie("is_login")
    # return rep
    request.session.flush() # 删除一条记录包括(session_key session_data expire_date)三个字段
    return redirect("happy:login")

# 注册
def hregister(request):
    if request.method == "POST":
        form = hforms.RegisterForm(request.POST)
        if form.is_valid():
            user = form.save() # 返回的对象取决于表单的类型，此处返回的是 ​​关联模型（User）的实例​​
            messages.success(request, '注册成功！请登录')
            return redirect('happy:login')
    else:
        form = hforms.RegisterForm()
    
    return render(request, 'register.html', {'form': form})

# 个人详情
@login_required
def hprofile(request):
    status = request.session.get("is_login")
    print(f"------profile------is_login:{status}")
    if not status:
        return redirect('/login/')
    return render(request, "profile.html")

def book(request):
    # pub_obj = models.Publish.objects.filter(pk=1).first()
    # book = models.Book.objects.create(title="葵花宝典", price=250, pub_date="2013-10-10", publish=pub_obj)

    # pub_obj = models.Publish.objects.filter(pk=1).first()
    # pk = pub_obj.pk
    # book = models.Book.objects.create(title="冲灵剑法", price=100, pub_date="2004-04-04", publish_id=pk)

    #------------------------多对多-------------------------
    # chong = models.Author.objects.filter(name="令狐冲").first()
    # ying = models.Author.objects.filter(name="任盈盈").first()
    # book = models.Book.objects.filter(title="菜鸟教程").first()
    # book.author.add(chong, ying) # 多对多的数据存储在中间表，命名为 happy_book_author
    # return HttpResponse(book)

    # book_obj = models.Book.objects.get(id=10) # Book 模型的实例对象
    # author_list = models.Author.objects.filter(id__gt=2) # QuerySet集合
    # book_obj.author.add(*author_list) # 多对多关系是在 book 表里设置的，所以通过 book 表关联增加就是正向

    # book_obj.author.add(*[1,3]) # 传对象id

    # author = models.Author.objects.filter(name="任盈盈").last()
    # book = models.Book.objects.filter(title="冲灵剑法").last()
    # author.book_set.add(book) # 多对多关系是在 book 表里设置的，所以通过 author 表关联增加就是反向,_set

    # pub = models.Publish.objects.filter(name="明教出版社").first()
    # aut = models.Author.objects.filter(name="任我行").first()
    # book = aut.book_set.create(title="吸星大法", price=300, pub_date="1999-9-19", publish=pub)

    # author_obj = models.Author.objects.get(id=3)
    # book_obj = models.Book.objects.get(id=10)
    # author_obj.book_set.remove(book_obj)

    # book = models.Book.objects.filter(title="菜鸟教程").first()
    # book.author.clear()
    # return HttpResponse("ok")

    #------------------------一对多-------------------------
    # book = models.Book.objects.filter(pk=10).first()
    # city = book.publish.city
    # print(city, type(city))

    # pub = models.Publish.objects.filter(name="明教出版社").first()
    # # bookset = pub.book_set.all()
    # bookdict = pub.book_set.values() 
    # print(bookdict, type(bookdict))

    # author = models.Author.objects.filter(name="令狐冲").first()
    # tel = author.au_detail.tel
    # print(tel, type(tel))

    # detail = models.AuthorDetail.objects.filter(addr="黑木崖").first()
    # name = detail.author.name
    # print(name, type(name))

    # book = models.Book.objects.filter(title="菜鸟教程").first()
    # author = book.author.all()
    # for a in author:
    #     print(a.name, a.au_detail.tel)
    
    # author = models.Author.objects.filter(name="任我行").first()
    # book = author.book_set.all()
    # for b in book:
    #     print(b.title, b.price)
    # return HttpResponse("ok")

    # res = models.Book.objects.filter(publish__name="明教出版社").values_list("title", "price")
    # res = models.Publish.objects.filter(name="明教出版社").values_list("book__title","book__price")
    # res = models.Book.objects.filter(author__name="任我行").values_list("title")
    # return HttpResponse(res)

    # book_dic = model_to_dict(book)
    # print(f"------------pub_obj 所有数据: {pub_obj.__dict__}")
    # print(f"------------{book_dic}")
    # print(f"------------{type(book)}")
    # return JsonResponse(book_dic)

    # res = models.Book.objects.aggregate(Avg("price"))
    # res = models.Book.objects.aggregate(max=Max("price"),min=Min("price"),c=Count("id"))
    # res = models.Publish.objects.values("name").annotate(in_price = Min("book__price"))
    # res = models.Book.objects.annotate(c = Count("author__name", distinct=True)).values("title","c")
    # res = models.Book.objects.annotate(c=Count("author__name")).filter(c__gt=1).values("title", "c")
    # res = models.Book.objects.filter(title__startswith="菜").annotate(c=Count("author")).values("title", "c")
    # res = models.Author.objects.annotate(total=Sum("book__price"), c=Count("book")).values("name", "total", "c").order_by("-c")
    
    # res = models.Emp.objects.filter(salary__gt=F("age")).values("name", "salary", "age")
    # res = models.Book.objects.update(price=F("price")+100)
    # res = models.Book.objects.filter(
    #     Q(price__gt=400) | 
    #     Q(title__startswith="菜") & ~Q(pub_date="2010-10-10")
    #     )
    res = models.Book.objects.filter(
        Q(price__gt=200)  & Q(pub_date__year__gt="2011"),
        title__startswith="菜"
        )
    print(res, type(res))
    return HttpResponse(res)

def add_emp(request):
    if request.method == "GET":
        form = hforms.EmpForm()
        return render(request, "add_emp.html", {"form": form})
    else:
        form = hforms.EmpForm(request.POST) #​​用 request.POST中提交的数据初始化一个 EmpForm实例​​。
        if form.is_valid():
            print(f"------data: {request.POST}")
            data = form.cleaned_data # 获取清洗后的数据（字典形式）
            print(f"------data: {data}")
            data.pop("r_salary") # 移除不需要的字段
            print(f"------data: {data}")

            models.Emp.objects.create(**data)
            return HttpResponse("提交成功")
        else:
            print(f"------error: {form.errors}") # 获取所有字段的错误信息
            clean_errors = form.errors.get("__all__") # 获取表单级错误
            print(f"------clean_errors: {clean_errors}")
            return render(
                request, 
                "add_emp.html", 
                {"form": form, "clean_errors": clean_errors}  # 回显表单和错误
            )
            