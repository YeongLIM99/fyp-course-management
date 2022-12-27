from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def home(request):
    return render(request, 'index/home.html', {'page_title': 'Home Page'})


def about(request):
    return render(request, 'index/about.html', {'page_title': 'About Page'})


def faq(request):
    return render(request, 'index/faq.html', {'page_title': 'FAQ Page'})
