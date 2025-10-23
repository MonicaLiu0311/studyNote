from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators import csrf

from my_test.models import Test

def search_post(request):
    result = Test.objects.filter(name=request.POST.get('query', '').strip())
    return render(request, 'search_post.html', {'result': result})
    