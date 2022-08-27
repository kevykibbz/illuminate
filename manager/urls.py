
from django.urls import path
from django import views
from . import views
from .views import *
from django.contrib.auth import views as auth_views
urlpatterns=[
    path('',views.home,name='dashboard'),
    path('about',views.about,name='about'),
    path('services',views.service,name='service'),
    path('gallary',views.gallary,name='gallary'),
    path('blog',views.blog,name='blog'),
    path('contact',Contact.as_view(),name='contact'),
]