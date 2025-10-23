from django.shortcuts import render

def hello(request):
    print(f'hello() 请求对象为： {request}')
    data_hello = 'Hello Django! I am Monica.' #｛"HTML变量名" : "views变量名"｝
    data_lists = ['Monica', 'Lily', 'Jon', 'Frank']
    data_leader = {'name': 'Cheney', 'age': 30}
    data_num = 1024
    data = {
        'hello':data_hello, 
        'name_list': data_lists, 
        'leader': data_leader,
        'num': data_num
    }
    return render(request, 'hello.html', data)