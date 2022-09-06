
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
    path('site/gallary',views.siteGallary,name='site gallary'),
    path('site/gallary/categories',views.siteGallaryCategories,name='site gallary categories'),
    path('add/images',views.addImages,name='add images'),
    path('add/gallary',addGallary.as_view(),name='add gallary'),
    path('edit/gallary/<int:id>',editGallary.as_view(),name='edit gallary'),
    path('delete/gallary/<int:id>',views.deleteGallary,name='delete gallary'),
    path('edit/category/<int:id>',editCategory.as_view(),name='edit category'),
    path('delete/category/<int:id>',views.deleteCategory,name='delete category'),
    path('blog',views.blog,name='blog'),
    path('contact',Contact.as_view(),name='contact'),
    path('accounts/login',Login.as_view(),name='login'),
    path('accounts/logout',views.user_logout,name='logout'),
    path('panel',views.panel,name='panel'),
    path('admins',views.admins,name='admins'),
    path('messages',views.messages,name='messages'),
    path('open/message/<int:id>',Reply.as_view(),name='reply'),
    path('add/admin',addAdmin.as_view(),name='admin add'),
    path('edit/admin/<int:id>',editAdmin.as_view(),name='edit admin'),
    path('delete/admin/<int:id>',views.deleteAdmin,name='delete admin'),
    path('calender',views.calender,name='calender'),
    path('general/site/settings',General.as_view(),name='general'),

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
    path('site/contact',views.siteContact,name='site contact'),
    path('site/working/days',views.siteWorking,name='site working days'),
    path('site/social/links',views.siteSocial,name='site social links'),


    #service
    path('site/services',views.siteService,name='site service'),
    path('add/service',addService.as_view(),name='add service'),
    path('edit/service/<int:id>',editService.as_view(),name='edit service'),
    path('delete/service/<int:id>',views.deleteService,name='delete service'),

    #about page settings
    path('site/about/page',aboutPage.as_view(),name='site about page'),

    #home page settings
    path('site/home/page',homePage.as_view(),name='site home page'),
    path('site/slider/images',views.sliderImages,name='slider images'),
    path('add/slider/image',addSlider.as_view(),name='add slider'),
    path('edit/slider/<int:id>',editSlider.as_view(),name='edit slider'),
    path('delete/slider/<int:id>',views.deleteSlider,name='delete slider'),

    #blog page
    path('site/blogs/page',views.blogsView,name='site blogs'),
    path('add/blog',blogAdd.as_view(),name='blog add'),
    path('edit/blog/<int:id>',editBlog.as_view(),name='edit blog'),
    path('delete/blog/<int:id>',views.deleteBlog,name='delete blog'),
    #read more
    path('read/more/<int:id>',readMore.as_view(),name='read more'),
]