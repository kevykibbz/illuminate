import dataclasses
from django.shortcuts import render
from manager.decorators import unauthenticated_user,allowed_users
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import *
from django.contrib.auth.models import User,Group,Permission
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render,get_object_or_404
from django.views.generic import View
from django.contrib.auth import authenticate,login,logout
from django.http import JsonResponse,HttpResponse,HttpResponseBadRequest
from installation.models import SiteConstants
from django.shortcuts import redirect
from .forms import *
from django.core.paginator import Paginator
from django.contrib.sites.shortcuts import get_current_site
from .addons import send_email,getSiteData
import json
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
from django.contrib.humanize.templatetags.humanize import intcomma
from django import template
import math
from django.utils.crypto import get_random_string
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.templatetags.static import static
from installation.models import SiteConstants
import re
from six.moves import urllib
from django.contrib.auth.hashers import make_password
import environ
env=environ.Env()
environ.Env.read_env()

# Create your views here.
def home(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    about=AboutModel.objects.all().last()
    home=HomeModel.objects.all().last()
    services=ServiceModel.objects.all().order_by("-id")[:3]
    sliders=SliderModel.objects.all()
    data={
        'title':f'Welcome to {obj.site_name}',
        'obj':obj,
        'data':request.user,
        'about':about,
        'services':services,
        'home':home,
        'sliders':sliders,
    }
    return render(request,'manager/index.html',context=data)

def about(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    about=AboutModel.objects.all().last()
    data={
        'title':'About us',
        'obj':obj,
        'data':request.user,
        'about':about,
    }
    return render(request,'manager/about.html',context=data)

def service(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    data=ServiceModel.objects.all().order_by("-id")
    paginator=Paginator(data,20)
    page_num=request.GET.get('page')
    services=paginator.get_page(page_num)
    data1={
        'title':'Our services',
        'obj':obj,
        'data':request.user,
        'count':paginator.count,
        'services':services,
    }
    return render(request,'manager/services.html',context=data1)

def gallary(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    categories=CategoryModel.objects.all()
    gallaries=GallaryModel.objects.all()
    data={
        'title':'Gallary',
        'obj':obj,
        'data':request.user,
        'categories':categories,
        'gallaries':gallaries,
    }
    return render(request,'manager/gallary.html',context=data)

def blog(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    blogs=BlogsModel.objects.all()
    data={
        'title':'Blog',
        'obj':obj,
        'data':request.user,
        'blogs':blogs,
    }
    return render(request,'manager/blog.html',context=data)

class Contact(View):
    def get(self ,request):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        form=UsersContactForm()
        data={
            'title':'Contact us',
            'obj':obj,
            'data':request.user,
            'form':form
        }
        return render(request,'manager/contact.html',context=data)
    def post(self,request):
        form=UsersContactForm(request.POST or None)
        if form.is_valid():
            usr=form.save(commit=False)
            usr.initials=form.cleaned_data.get('name')[0].upper()
            usr.save()
            return JsonResponse({'valid':True,'message':'Message sent!'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')


#readMore
class readMore(View):
    def get(self ,request,id):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        user=BlogsModel.objects.get(id=id)
        blogs=BlogsModel.objects.all().exclude(id=id).order_by("-id")
        comments=CommentModel.objects.filter(blog_id=id).order_by('-id')[:10]
        count=CommentModel.objects.filter(blog_id=id).count()
        form=CommentForm()
        data={
            'title':f'Read more | {user.blog_head}',
            'obj':obj,
            'data':request.user,
            'form':form,
            'comments':comments,
            'blogs':blogs,
            'count':count,
            'current':user,
        }
        return render(request,'manager/read_more.html',context=data)
    def post(self,request,id):
        form=CommentForm(request.POST or None)
        if form.is_valid():
            usr=form.save(commit=False)
            usr.blog_id=id
            usr.initials=form.cleaned_data.get('name')[0].upper()
            usr.save()
            return JsonResponse({'valid':True,'message':'Comment posted!'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')



#Login
@method_decorator(unauthenticated_user,name='dispatch')
class Login(View):
    def get(self,request):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        if request.user.is_authenticated:
           initials=request.user.first_name[0].upper()+request.user.last_name[0].upper()
        else:
            initials='AU'
        form=UserLoginForm()
        data={
            'title':'Login',
            'obj':obj,
            'data':request.user,
            'form':form,
            'login':True,
            'initials':initials
        }
        return render(request,'panel/login.html',context=data)
    def post(self,request):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            key=request.POST['username']
            password=request.POST['password']
            if key:
                if password:
                    regex=re.compile(r'([A-Za-z0-9+[.-_]])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
                    if re.fullmatch(regex,key):
                        #email address
                        if User.objects.filter(email=key).exists():
                            data=User.objects.get(email=key)
                            user=authenticate(username=data.username,password=password)
                        else:
                            form_errors={"username": ["Invalid email address."]}
                            return JsonResponse({'valid':False,'form_errors':form_errors},content_type="application/json")
                    else:
                        #username
                        if User.objects.filter(username=key).exists():
                            user=authenticate(username=key,password=password)
                        else:
                            form_errors={"username": ["Invalid username."]}
                            return JsonResponse({'valid':False,'form_errors':form_errors},content_type="application/json")
                        
                    if user is not None:
                        if 'remember' in request.POST:
                           request.session.set_expiry(1209600) #two weeeks
                        else:
                           request.session.set_expiry(0) 
                        login(request,user)
                        return JsonResponse({'valid':True,'feedback':'success:Login Successfully.'},content_type="application/json")
                    form_errors={"password": ["Password is incorrect."]}
                    return JsonResponse({'valid':False,'form_errors':form_errors},content_type="application/json")
                else:
                    form_errors={"password": ["Password is required."]}
                    return JsonResponse({'valid':False,'form_errors':form_errors},content_type="application/json")
            else:
                form_errors={"username": ["Username/Email Address is required."]}
                return JsonResponse({'valid':False,'form_errors':form_errors},content_type="application/json")

#logout
def user_logout(request):
    logout(request)
    return redirect('/accounts/login')
#screenLock
def screenLock(request,username):
    logout(request)
    return redirect(f'/unlock/screen/{username}')

#screenUnlock
def screenUnlock(request,username):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    try:
        data=User.objects.get(username__exact=username)
        data={
            'title':'Screen Unlock',
            'obj':obj,
            'data':data,
        }
        return render(request,'panel/screen_unlock.html',context=data)       
    except User.DoesNotExist:
        data={
                'title':'Error | Page Not Found',
                'obj':obj
        }
        return render(request,'manager/404.html',context=data,status=404)








#panel
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def panel(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
    count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
    data={
        'title':'Panel',
        'obj':obj,
        'data':request.user,
        'messages':messages,
        'count':count
    }
    return render(request,'panel/index.html',context=data)

#messages
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def messages(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    data=ContactModel.objects.filter(is_read=False).order_by("-id")
    paginator=Paginator(data,10)
    page_num=request.GET.get('page')
    messages=paginator.get_page(page_num)
    data={
        'title':'Messages',
        'obj':obj,
        'data':request.user,
        'messages':messages,
        'count':paginator.count
    }
    return render(request,'panel/messages.html',context=data)

#Reply
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class Reply(View):
    def get(self,request,id):
        obj=SiteConstants.objects.count()
        if obj == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        try:
            message=ContactModel.objects.get(id__exact=id)
            messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
            count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
            form=UsersReplyForm(instance=message)
            data={
                'title':f'Message#{message.name}',
                'obj':obj,
                'data':request.user,
                'form':form,
                'message':message,
                'messages':messages,
                'count':count,
            }
            return render(request,'panel/reply.html',context=data)      
        except ContactModel.DoesNotExist:
            data={
                    'title':'Error | Page Not Found',
                    'obj':obj
            }
            return render(request,'manager/404.html',context=data,status=404)
    def post(self,request,id):
        message=ContactModel.objects.get(id__exact=id)
        form=UsersReplyForm(request.POST or None,instance=message)
        if form.is_valid():
            obj=SiteConstants.objects.all()[0]
            usr=form.save(commit=False)
            usr.is_read=True
            usr.save()
            subject=f'Reply to{message.subject}'
            email=message.email
            message={
                        'user':message.name,
                        'site_name':obj.site_name,
                        'site_url':obj.site_url,
                        'address':obj.address,
                        'phone':obj.phone,
                        'message':form.cleaned_data.get('reply',None)
                    }
            template='emails/reply.html'
            send_email(subject,email,message,template)
            return JsonResponse({'valid':True,'message':'Feedback sent!'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')
       
#calender
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def calender(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
    count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
    data={
        'title':'Calender',
        'obj':obj,
        'data':request.user,
        'messages':messages,
        'count':count,
    }
    return render(request,'panel/calender.html',context=data)



#General
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class General(View):
    def get(self,request):
        obj=SiteConstants.objects.count()
        if obj == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
        count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
        form1=SiteForm(instance=obj)
        form2=AddressConfigForm(instance=obj)
        form3=UserSocialForm(instance=obj)
        form4=WorkingConfigForm(instance=obj)
        data={
            'title':'General site settings',
            'obj':obj,
            'data':request.user,
            'messages':messages,
            'count':count,
            'form1':form1,
            'form2':form2,
            'form3':form3,
            'form4':form4,
        }
        return render(request,'panel/general.html',context=data) 
    def post(self,request,*args , **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            instance_data=SiteConstants.objects.all().first()
            form=SiteForm(request.POST,request.FILES or None , instance=instance_data)
            if form.is_valid():
                form.save()
                return JsonResponse({'valid':True,'message':'data saved successfully'},status=200,content_type='application/json')
            else:
                return JsonResponse({'valid':False,'uform_errors':form.errors},status=200,content_type='application/json')

#admins
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def admins(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    data=User.objects.filter(extendedauthuser__role='admins').order_by('-id')
    messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
    count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
    paginator=Paginator(data,10)
    page_num=request.GET.get('page')
    admins=paginator.get_page(page_num)
    data={
        'title':'Site Admins',
        'obj':obj,
        'data':request.user,
        'admins':admins,
        'count':count,
        'messages':messages,
        'acount':paginator.count,
    }
    return render(request,'panel/admins.html',context=data)

#siteContact
@login_required(login_url='accounts/login/')
@allowed_users(allowed_roles=['admins'])
def siteContact(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        instance_data=SiteConstants.objects.all().first()
        form=AddressConfigForm(request.POST or None , instance=instance_data)
        if form.is_valid():
            form.save()
            return JsonResponse({'valid':True,'message':'data saved successfully'},status=200,content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},status=200,content_type='application/json')

#siteWorking
@login_required(login_url='accounts/login/')
@allowed_users(allowed_roles=['admins'])
def siteWorking(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        instance_data=SiteConstants.objects.all().first()
        form=WorkingConfigForm(request.POST, request.FILES or None , instance=instance_data)
        if form.is_valid():
            form.save()
            return JsonResponse({'valid':True,'message':'data saved successfully'},status=200,content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},status=200,content_type='application/json')


#siteSocial
@login_required(login_url='accounts/login/')
@allowed_users(allowed_roles=['admins'])
def siteSocial(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        instance_data=SiteConstants.objects.all().first()
        form=UserSocialForm(request.POST or None , instance=instance_data)
        if form.is_valid():
            form.save()
            return JsonResponse({'valid':True,'message':'data saved successfully'},status=200,content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},status=200,content_type='application/json')

@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class addAdmin(View):
    def get(self ,request):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
        count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
        form=users_registerForm()
        eform=EProfileForm()
        data={
            'title':'Add new admin',
            'obj':obj,
            'data':request.user,
            'count':count,
            'messages':messages,
            'form':form,
            'eform':eform
        }
        return render(request,'panel/add_admin.html',context=data)
    def post(self,request):
        if  request.headers.get('x-requested-with') == 'XMLHttpRequest':
            uform=users_registerForm(request.POST or None)
            eform=EProfileForm(request.POST , request.FILES or None)
            if uform.is_valid() and  eform.is_valid():
                userme=uform.save(commit=False)
                userme.is_active = True
                userme.save()
                extended=eform.save(commit=False)
                extended.user=userme
                extended.initials=uform.cleaned_data.get('first_name')[0].upper()+uform.cleaned_data.get('last_name')[0].upper()
                extended.save()
                user=User.objects.get(email__exact=uform.cleaned_data.get('email'))
                ct=ContentType.objects.get_for_model(ExtendedAuthUser)
                role=eform.cleaned_data.get('role')
                if 'admins' in role:
                    if not Group.objects.filter(name='admins').exists():
                        group=Group.objects.create(name='admins')
                        group.user_set.add(userme)
                        p1=Permission.objects.filter(content_type=ct).all()[0]
                        p3=Permission.objects.filter(content_type=ct).all()[2]
                        group.permissions.add(p1)
                        group.permissions.add(p3)
                        group.save()
                    else:
                        group=Group.objects.get(name__icontains='admins')
                        group.user_set.add(userme)
                        group.save()
                else:
                    if not Group.objects.filter(name='employee').exists():
                        group=Group.objects.create(name='employee')
                        group.user_set.add(userme)
                        p1=Permission.objects.filter(content_type=ct).all()[0]
                        p3=Permission.objects.filter(content_type=ct).all()[2]
                        group.permissions.add(p1)
                        group.permissions.add(p3)
                        group.save()
                    else:
                        group=Group.objects.get(name__icontains='employee')
                        group.user_set.add(userme)
                        group.save()
                return JsonResponse({'valid':True,'message':'user added successfully','profile_pic':user.extendedauthuser.profile_pic.url},content_type="application/json")
            else:
                return JsonResponse({'valid':False,'uform_errors':uform.errors,'eform_errors':eform.errors},content_type="application/json")

@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class editAdmin(View):
    def get(self ,request,id):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        user=User.objects.get(id=id)
        form=CurrentLoggedInUserProfileChangeForm(instance=user)
        eform=CurrentExtUserProfileChangeForm(instance=user.extendedauthuser)
        messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
        count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
        if user.extendedauthuser.role == 'admins':
            eform.fields['role'].choices=[('admins','Admin'),]
            eform.fields['role'].initial=[0]
        else:
            eform.fields['role'].choices=[('employee','Employee'),]
            eform.fields['role'].initial=[0]
        data={
            'title':f'Edit admin | {user.get_full_name()}',
            'obj':obj,
            'data':request.user,
            'form':form,
            'admin':user,
            'count':count,
            'messages':messages,
            'eform':eform,
            'edit':True
        }
        return render(request,'panel/add_admin.html',context=data)

    def post(self,request,id,*args ,**kwargs):
        user=User.objects.get(id=id)
        form=CurrentLoggedInUserProfileChangeForm(request.POST or None,instance=user)
        eform=CurrentExtUserProfileChangeForm(request.POST,request.FILES or None,instance=user.extendedauthuser)
        if form.is_valid() and eform.is_valid():
            form.save()
            eform.save()
            return JsonResponse({'valid':True,'message':'Admin updated successfuly.'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors,'eform_errors':eform.errors,},content_type='application/json')

#deleteAdmin
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def deleteAdmin(request,id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            obj=User.objects.get(id__exact=id)
            obj.delete() 
            return JsonResponse({'valid':True,'message':'Admin deleted successfully.','id':id},content_type='application/json')       
        except User.DoesNotExist:
            return JsonResponse({'valid':False,'message':'Admin does not exist'},content_type='application/json')


#employees
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def employees(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    data=User.objects.filter(extendedauthuser__role='employee').order_by('-id')
    messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
    count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
    paginator=Paginator(data,10)
    page_num=request.GET.get('page')
    employees=paginator.get_page(page_num)
    data={
        'title':'Site Employees',
        'obj':obj,
        'data':request.user,
        'employees':employees,
        'acount':paginator.count,
        'messages':messages,
        'count':count,

    }
    return render(request,'panel/employees.html',context=data)

@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class addEmployee(View):
    def get(self ,request):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
        count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
        form=users_registerForm()
        eform=EProfileForm()
        data={
            'title':'Add new employee',
            'obj':obj,
            'data':request.user,
            'form':form,
            'eform':eform,
            'messages':messages,
            'count':count,
        }
        return render(request,'panel/add_employee.html',context=data)
    def post(self,request):
        if  request.headers.get('x-requested-with') == 'XMLHttpRequest':
            uform=users_registerForm(request.POST or None)
            eform=EProfileForm(request.POST , request.FILES or None)
            if uform.is_valid() and  eform.is_valid():
                userme=uform.save(commit=False)
                userme.is_active = True
                userme.save()
                extended=eform.save(commit=False)
                extended.user=userme
                extended.initials=uform.cleaned_data.get('first_name')[0].upper()+uform.cleaned_data.get('last_name')[0].upper()
                extended.save()
                user=User.objects.get(email__exact=uform.cleaned_data.get('email'))
                ct=ContentType.objects.get_for_model(ExtendedAuthUser)
                role=eform.cleaned_data.get('role')
                if 'admins' in role:
                    if not Group.objects.filter(name='admins').exists():
                        group=Group.objects.create(name='admins')
                        group.user_set.add(userme)
                        p1=Permission.objects.filter(content_type=ct).all()[0]
                        p3=Permission.objects.filter(content_type=ct).all()[2]
                        group.permissions.add(p1)
                        group.permissions.add(p3)
                        group.save()
                    else:
                        group=Group.objects.get(name__icontains='admins')
                        group.user_set.add(userme)
                        group.save()
                else:
                    if not Group.objects.filter(name='employee').exists():
                        group=Group.objects.create(name='employee')
                        group.user_set.add(userme)
                        p1=Permission.objects.filter(content_type=ct).all()[0]
                        p3=Permission.objects.filter(content_type=ct).all()[2]
                        group.permissions.add(p1)
                        group.permissions.add(p3)
                        group.save()
                    else:
                        group=Group.objects.get(name__icontains='employee')
                        group.user_set.add(userme)
                        group.save()
                return JsonResponse({'valid':True,'message':'user added successfully','profile_pic':user.extendedauthuser.profile_pic.url},content_type="application/json")
            else:
                return JsonResponse({'valid':False,'uform_errors':uform.errors,'eform_errors':eform.errors},content_type="application/json")

@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class editEmployee(View):
    def get(self ,request,id):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        user=User.objects.get(id=id)
        form=CurrentLoggedInUserProfileChangeForm(instance=user)
        eform=CurrentExtUserProfileChangeForm(instance=user.extendedauthuser)
        messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
        count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
        if user.extendedauthuser.role == 'admins':
            eform.fields['role'].choices=[('admins','Admin'),]
            eform.fields['role'].initial=[0]
        else:
            eform.fields['role'].choices=[('employee','Employee'),]
            eform.fields['role'].initial=[0]
        data={
            'title':f'Edit employee | {user.get_full_name()}',
            'obj':obj,
            'data':request.user,
            'form':form,
            'admin':user,
            'eform':eform,
            'edit':True,
            'count':count,
            'messages':messages,
        }
        return render(request,'panel/add_employee.html',context=data)

    def post(self,request,id,*args ,**kwargs):
        user=User.objects.get(id=id)
        form=CurrentLoggedInUserProfileChangeForm(request.POST or None,instance=user)
        eform=CurrentExtUserProfileChangeForm(request.POST,request.FILES or None,instance=user.extendedauthuser)
        if form.is_valid() and eform.is_valid():
            form.save()
            eform.save()
            return JsonResponse({'valid':True,'message':'Employee updated successfuly.'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors,'eform_errors':eform.errors,},content_type='application/json')

#deleteEmployee
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def deleteEmployee(request,id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            obj=User.objects.get(id__exact=id)
            obj.delete() 
            return JsonResponse({'valid':True,'message':'Employee deleted successfully.','id':id},content_type='application/json')       
        except User.DoesNotExist:
            return JsonResponse({'valid':False,'message':'Employee does not exist'},content_type='application/json')


#ProfileView
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
class ProfileView(View):
    def get(self,request,username):
        obj=SiteConstants.objects.count()
        if obj == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        try:
            user=User.objects.get(username__exact=username)
            form=CurrentLoggedInUserProfileChangeForm(request.POST or None,instance=user)
            eform=CurrentExtUserProfileChangeForm(request.POST or None,instance=user.extendedauthuser)
            messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
            count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
            passform=UserPasswordChangeForm()
            profileform=ProfilePicForm()
            if request.user.extendedauthuser.role == 'admins':
                eform.fields['role'].choices=[('admins','Admin'),]
                eform.fields['role'].initial=[0]
            else:
                eform.fields['role'].choices=[('employee','Employee'),]
                eform.fields['role'].initial=[0]
            data={
                'title':f'Edit profile | {user.get_full_name()}',
                'obj':obj,
                'data':request.user,
                'form':form,
                'eform':eform,
                'count':count,
                'messages':messages,
                'editor':user,
                'passform':passform,
                'profileform':profileform
            }
            return render(request,'panel/profile.html',context=data)
        except User.DoesNotExist:
            return render(request,'manager/404.html',{'title':'Error | Bad Request'},status=400)
 
    def post(self,request,username,*args ,**kwargs):
        user=User.objects.get(username__exact=username)
        form=CurrentLoggedInUserProfileChangeForm(request.POST or None,instance=user)
        eform=CurrentExtUserProfileChangeForm(request.POST,request.FILES or None,instance=user.extendedauthuser)
        if form.is_valid() and eform.is_valid():
            form.save()
            eform.save()
            return JsonResponse({'valid':True,'message':'Profile updated successfully.','profile_pic':True},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors,'eform_errors':eform.errors,},content_type='application/json')



#passwordChange
@login_required(login_url='/accounts/login')
def passwordChange(request,username):
    if request.method=='POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        passform=UserPasswordChangeForm(request.POST or None,instance=request.user)
        if passform.is_valid():
            user=User.objects.get(username__exact=request.user.username)
            user.password=make_password(passform.cleaned_data.get('password1'))
            user.save()
            update_session_auth_hash(request,request.user)
            return JsonResponse({'valid':True,'message':'Password changed successfully'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':passform.errors},content_type='application/json')



#profile pic
@login_required(login_url='/accounts/login')
def profilePic(request):
    if request.method=='POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form=ProfilePicForm(request.FILES or None,instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({'valid':True,'message':'profile picture changed successfully'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')



#siteGallary
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def siteGallary(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    data=GallaryModel.objects.order_by("-id")
    messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
    count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
    paginator=Paginator(data,20)
    page_num=request.GET.get('page')
    gallaries=paginator.get_page(page_num)
    data={
        'title':'Site Gallary',
        'obj':obj,
        'data':request.user,
        'count':count,
        'messages':messages,
        'acount':paginator.count,
        'gallaries':gallaries,
    }
    return render(request,'panel/site_gallary.html',context=data)

#addGallary
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class addGallary(View):
    def get(self ,request):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
        count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
        categories=CategoryModel.objects.all()
        form=CategoryForm()
        form2=GallaryForm()
        data={
            'title':'Add images',
            'obj':obj,
            'data':request.user,
            'form':form,
            'form2':form2,
            'count':count,
            'messages':messages,
            'categories':categories,
        }
        return render(request,'panel/add_gallary.html',context=data)
    def post(self,request,*args ,**kwargs):
        form=CategoryForm(request.POST or None)
        if form.is_valid():
            cat=form.save(commit=False)
            cat.user_id=request.user.pk
            cat.save()
            return JsonResponse({'valid':True,'message':'Category created successfully.','gallary':True},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')


#addImages
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def addImages(request):
    if request.method=='POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form=GallaryForm(request.POST,request.FILES or None)
        if form.is_valid():
            cat=form.save(commit=False)
            cat.user_id=request.user.pk
            cat.save()
            return JsonResponse({'valid':True,'message':'Image uploded successfully'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')



#editGallary
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class editGallary(View):
    def get(self ,request,id):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        user=GallaryModel.objects.get(id=id)
        form=CategoryForm()
        form2=GallaryForm(instance=user)
        messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
        count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
        categories=CategoryModel.objects.all()
        data={
            'title':f'Edit gallary | {user.category}',
            'obj':obj,
            'data':request.user,
            'form':form,
            'form2':form2,
            'categories':categories,
            'count':count,
            'messages':messages,
            'gallary_edit':True
        }
        return render(request,'panel/add_gallary.html',context=data)

    def post(self,request,id,*args ,**kwargs):
        user=GallaryModel.objects.get(id=id)
        form=GallaryForm(request.POST,request.FILES or None,instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({'valid':True,'message':'Image gallary updated successfuly.'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')

#deleteGallary
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def deleteGallary(request,id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            obj=GallaryModel.objects.get(id__exact=id)
            obj.delete() 
            return JsonResponse({'valid':True,'message':'Image gallary deleted successfully.','id':id},content_type='application/json')       
        except GallaryModel.DoesNotExist:
            return JsonResponse({'valid':False,'message':'Item does not exist'},content_type='application/json')

#siteGallaryCategories
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def siteGallaryCategories(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    data=CategoryModel.objects.order_by("-id")
    messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
    count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
    paginator=Paginator(data,20)
    page_num=request.GET.get('page')
    categories=paginator.get_page(page_num)
    data={
        'title':'Site Gallary Categories',
        'obj':obj,
        'data':request.user,
        'count':count,
        'messages':messages,
        'acount':paginator.count,
        'categories':categories,
    }
    return render(request,'panel/site_gallary_categories.html',context=data)

#editCategory
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class editCategory(View):
    def get(self ,request,id):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        user=CategoryModel.objects.get(id=id)
        form=CategoryForm(instance=user)
        form2=GallaryForm()
        messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
        count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
        data={
            'title':f'Edit Category | {user.category}',
            'obj':obj,
            'data':request.user,
            'form':form,
            'form2':form2,
            'count':count,
            'messages':messages,
            'category_edit':True
        }
        return render(request,'panel/add_gallary.html',context=data)

    def post(self,request,id,*args ,**kwargs):
        user=CategoryModel.objects.get(id=id)
        form=CategoryForm(request.POST or None,instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({'valid':True,'message':'Gallary category updated successfuly.'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')

#deleteCategory
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def deleteCategory(request,id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            obj=CategoryModel.objects.get(id__exact=id)
            obj.delete() 
            return JsonResponse({'valid':True,'message':'Gallary category deleted successfully.','id':id},content_type='application/json')       
        except CategoryModel.DoesNotExist:
            return JsonResponse({'valid':False,'message':'Item does not exist'},content_type='application/json')


#siteService
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def siteService(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    data=ServiceModel.objects.order_by("-id")
    messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
    count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
    paginator=Paginator(data,20)
    page_num=request.GET.get('page')
    services=paginator.get_page(page_num)
    data={
        'title':'Site Services',
        'obj':obj,
        'data':request.user,
        'count':count,
        'messages':messages,
        'acount':paginator.count,
        'services':services,
    }
    return render(request,'panel/site_service.html',context=data)

#addService
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class addService(View):
    def get(self ,request):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
        count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
        form=ServiceForm()
        data={
            'title':'Add Service',
            'obj':obj,
            'data':request.user,
            'form':form,
            'count':count,
            'messages':messages,
        }
        return render(request,'panel/add_service.html',context=data)
    def post(self,request,*args ,**kwargs):
        form=ServiceForm(request.POST,request.FILES or None)
        if form.is_valid():
            cat=form.save(commit=False)
            cat.user_id=request.user.pk
            cat.save()
            return JsonResponse({'valid':True,'message':'Service created successfully.'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')


#editService
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class editService(View):
    def get(self ,request,id):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        user=ServiceModel.objects.get(id=id)
        form=ServiceForm(instance=user)
        messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
        count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
        data={
            'title':f'Edit Service | {user.title}',
            'obj':obj,
            'data':request.user,
            'form':form,
            'count':count,
            'messages':messages,
            'service_edit':True
        }
        return render(request,'panel/add_service.html',context=data)

    def post(self,request,id,*args ,**kwargs):
        user=ServiceModel.objects.get(id=id)
        form=ServiceForm(request.POST or None,instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({'valid':True,'message':'Site Service updated successfuly.'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')

#deleteService
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def deleteService(request,id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            obj=ServiceModel.objects.get(id__exact=id)
            obj.delete() 
            return JsonResponse({'valid':True,'message':'Site service deleted successfully.','id':id},content_type='application/json')       
        except ServiceModel.DoesNotExist:
            return JsonResponse({'valid':False,'message':'Item does not exist'},content_type='application/json')


#aboutPage
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class aboutPage(View):
    def get(self,request):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
        count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
        about=AboutModel.objects.all().last()
        if AboutModel.objects.count() > 0:
            form=AboutForm(instance=AboutModel.objects.all().last())
        else:
            form=AboutForm()
        data={
            'title':'Site About Page Settings',
            'obj':obj,
            'data':request.user,
            'count':count,
            'messages':messages,
            'about':about,
            'form':form,
        }
        return render(request,'panel/about.html',context=data)

    def post(self,request,*args ,**kwargs):
        if AboutModel.objects.count() > 0:
            form=AboutForm(request.POST,request.FILES or None,instance=AboutModel.objects.all().last())
            if form.is_valid():
                form.save()
                return JsonResponse({'valid':True,'message':'Site about page updated successfuly.','about':True},content_type='application/json')
            else:
                return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')
        else:
            form=AboutForm(request.POST,request.FILES or None)
            if form.is_valid():
                cat=form.save(commit=False)
                cat.user_id=request.user.pk
                cat.save()
                return JsonResponse({'valid':True,'message':'Site about page updated successfuly.','about':True},content_type='application/json')
            else:
                return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')

#homePage
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class homePage(View):
    def get(self,request):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
        count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
        home=HomeModel.objects.all().last()
        if HomeModel.objects.count() > 0:
            form=HomeForm(instance=HomeModel.objects.all().last())
        else:
            form=HomeForm()
        data={
            'title':'Site Home Page Settings',
            'obj':obj,
            'data':request.user,
            'count':count,
            'messages':messages,
            'home':home,
            'form':form,
        }
        return render(request,'panel/home.html',context=data)

    def post(self,request,*args ,**kwargs):
        if HomeModel.objects.count() > 0:
            form=HomeForm(request.POST,request.FILES or None,instance=HomeModel.objects.all().last())
            if form.is_valid():
                form.save()
                return JsonResponse({'valid':True,'message':'Site home page updated successfuly.','about':True},content_type='application/json')
            else:
                return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')
        else:
            form=HomeForm(request.POST,request.FILES or None)
            if form.is_valid():
                cat=form.save(commit=False)
                cat.user_id=request.user.pk
                cat.save()
                return JsonResponse({'valid':True,'message':'Site home page updated successfuly.','about':True},content_type='application/json')
            else:
                return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')

#sliderImages
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def sliderImages(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    sliders=SliderModel.objects.order_by("-id")
    messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
    count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
    data={
        'title':'Site home page slider images',
        'obj':obj,
        'data':request.user,
        'count':count,
        'messages':messages,
        'sliders':sliders,
    }
    return render(request,'panel/slider_images.html',context=data)

#addSlider
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class addSlider(View):
    def get(self,request):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
        count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
        form=SliderForm()
        data={
            'title':'Add slider image',
            'obj':obj,
            'data':request.user,
            'count':count,
            'messages':messages,
            'home':home,
            'form':form,
        }
        return render(request,'panel/add_slider.html',context=data)

    def post(self,request,*args ,**kwargs):
        form=SliderForm(request.POST,request.FILES or None)
        if form.is_valid():
            cat=form.save(commit=False)
            cat.user_id=request.user.pk
            cat.save()
            return JsonResponse({'valid':True,'message':'Site home page slider images  updated successfuly.','about':True},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')

#editSlider
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class editSlider(View):
    def get(self ,request,id):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        user=SliderModel.objects.get(id=id)
        form=SliderForm(instance=user)
        messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
        count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
        data={
            'title':f'Edit Slider | {user.slider_head}',
            'obj':obj,
            'data':request.user,
            'form':form,
            'count':count,
            'messages':messages,
            'slider_edit':True
        }
        return render(request,'panel/add_slider.html',context=data)

    def post(self,request,id,*args ,**kwargs):
        user=SliderModel.objects.get(id=id)
        form=SliderForm(request.POST or None,instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({'valid':True,'message':'Site home page slider image updated successfuly.'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')

#deleteSlider
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def deleteSlider(request,id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            obj=SliderModel.objects.get(id__exact=id)
            obj.delete() 
            return JsonResponse({'valid':True,'message':'Site home page slider image deleted successfully.','id':id},content_type='application/json')       
        except SliderModel.DoesNotExist:
            return JsonResponse({'valid':False,'message':'Item does not exist'},content_type='application/json')

#blogsView
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def blogsView(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    blogs=BlogsModel.objects.order_by("-id")
    messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
    count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
    data={
        'title':'Site blogs settings',
        'obj':obj,
        'data':request.user,
        'count':count,
        'messages':messages,
        'blogs':blogs,
    }
    return render(request,'panel/blogs.html',context=data)

#blogAdd
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class blogAdd(View):
    def get(self,request):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
        count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
        form=BlogsForm()
        data={
            'title':'Add blog',
            'obj':obj,
            'data':request.user,
            'count':count,
            'messages':messages,
            'home':home,
            'form':form,
        }
        return render(request,'panel/add_blog.html',context=data)

    def post(self,request,*args ,**kwargs):
        form=BlogsForm(request.POST,request.FILES or None)
        if form.is_valid():
            cat=form.save(commit=False)
            cat.user_id=request.user.pk
            cat.posted_by=request.user.get_full_name()
            cat.save()
            return JsonResponse({'valid':True,'message':'Site blog page created successfuly.'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')


#editBlog
@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class editBlog(View):
    def get(self ,request,id):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        user=BlogsModel.objects.get(id=id)
        form=BlogsForm(instance=user)
        messages=ContactModel.objects.filter(is_read=False).order_by("-id")[:3]
        count=ContactModel.objects.filter(is_read=False).order_by("-id").count()
        data={
            'title':f'Edit blog | {user.blog_head}',
            'obj':obj,
            'data':request.user,
            'form':form,
            'count':count,
            'messages':messages,
            'slider_edit':True
        }
        return render(request,'panel/add_blog.html',context=data)

    def post(self,request,id,*args ,**kwargs):
        user=SliderModel.objects.get(id=id)
        form=BlogsForm(request.POST or None,instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({'valid':True,'message':'Site blog page item updated successfuly.'},content_type='application/json')
        else:
            return JsonResponse({'valid':False,'uform_errors':form.errors},content_type='application/json')

#deleteBlog
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def deleteBlog(request,id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            obj=BlogsModel.objects.get(id__exact=id)
            obj.delete() 
            return JsonResponse({'valid':True,'message':'ite blog page item  deleted successfully.','id':id},content_type='application/json')       
        except BlogsModel.DoesNotExist:
            return JsonResponse({'valid':False,'message':'Item does not exist'},content_type='application/json')