from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='index-home'),
    path('faq/', views.faq, name='index-faq')
]