
from django.urls import path
from django import views
from . import views
from .views import *
from django.contrib.auth import views as auth_views
urlpatterns=[
    path('',views.home,name='dashboard'),
]