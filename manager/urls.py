
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
    path('accounts/login',Login.as_view(),name='login'),
    path('accounts/logout',views.user_logout,name='logout'),
    path('panel',views.panel,name='panel'),
    path('admins',views.admins,name='admins'),
    path('add/admin',addAdmin.as_view(),name='admin add'),
    path('edit/admin/<int:id>',editAdmin.as_view(),name='edit admin'),
    path('delete/admin/<int:id>',views.deleteAdmin,name='delete admin'),

    path('employees',views.employees,name='employees'),
    path('add/employee',addEmployee.as_view(),name='employee add'),
    path('edit/employee/<int:id>',editEmployee.as_view(),name='edit employee'),
    path('delete/employee/<int:id>',views.deleteEmployee,name='delete employee'),
    path('lock/screen/<str:username>',views.screenLock,name='lock screen'),
    path('unlock/screen/<str:username>',views.screenUnlock,name='unlock screen'),
    path('user/password/change/<str:username>',views.passwordChange,name='user password change'),
    path('user/profile/picture/change',views.profilePic,name='user profile picture change'),

    path('<str:username>',ProfileView.as_view(),name='profile'),
    path('accounts/reset/password',auth_views.PasswordResetView.as_view(form_class=UserResetPassword,template_name='panel/password_reset.html'),name='reset_password'),
    path('accounts/reset/password/done',auth_views.PasswordResetDoneView.as_view(template_name='panel/password_reset_done.html'),name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>',auth_views.PasswordResetConfirmView.as_view(template_name='panel/password_reset_confirm.html'),name='password_reset_confirm'),
    path('accounts/reset/password/complete',auth_views.PasswordResetCompleteView.as_view(template_name='panel/password_reset_complete.html'),name='password_reset_complete'),
]