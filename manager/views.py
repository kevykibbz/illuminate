import dataclasses
from django.shortcuts import render
from manager.decorators import unauthenticated_user,allowed_users
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import ExtendedAuthUser
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
from manager.addons import send_email
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
    data={
        'title':f'Welcome to {obj.site_name}',
        'obj':obj,
        'data':request.user,
    }
    return render(request,'manager/index.html',context=data)

def about(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    data={
        'title':'About us',
        'obj':obj,
        'data':request.user,
    }
    return render(request,'manager/about.html',context=data)

def service(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    data={
        'title':'Our services',
        'obj':obj,
        'data':request.user,
    }
    return render(request,'manager/services.html',context=data)

def gallary(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    data={
        'title':'Gallary',
        'obj':obj,
        'data':request.user,
    }
    return render(request,'manager/gallary.html',context=data)

def blog(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    data={
        'title':'Blog',
        'obj':obj,
        'data':request.user,
    }
    return render(request,'manager/blog.html',context=data)

class Contact(View):
    def get(self ,request):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        data={
            'title':'Contact us',
            'obj':obj,
            'data':request.user,
        }
        return render(request,'manager/contact.html',context=data)


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
def panel(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    data={
        'title':'Panel',
        'obj':obj,
        'data':request.user,
    }
    return render(request,'panel/index.html',context=data)

#admins
@login_required(login_url='/accounts/login')
@allowed_users(allowed_roles=['admins'])
def admins(request):
    if SiteConstants.objects.count() == 0:
        return redirect('/installation/')
    obj=SiteConstants.objects.all()[0]
    data=User.objects.filter(extendedauthuser__role='admins').order_by('-id')
    paginator=Paginator(data,10)
    page_num=request.GET.get('page')
    admins=paginator.get_page(page_num)
    data={
        'title':'Site Admins',
        'obj':obj,
        'data':request.user,
        'admins':admins,
        'count':paginator.count,
    }
    return render(request,'panel/admins.html',context=data)


@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class addAdmin(View):
    def get(self ,request):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        form=users_registerForm()
        eform=EProfileForm()
        data={
            'title':'Add new admin',
            'obj':obj,
            'data':request.user,
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
    paginator=Paginator(data,10)
    page_num=request.GET.get('page')
    employees=paginator.get_page(page_num)
    data={
        'title':'Site Employees',
        'obj':obj,
        'data':request.user,
        'employees':employees,
        'count':paginator.count,
    }
    return render(request,'panel/employees.html',context=data)

@method_decorator(login_required(login_url='/accounts/login'),name='dispatch')
@method_decorator(allowed_users(allowed_roles=['admins']),name='dispatch')
class addEmployee(View):
    def get(self ,request):
        if SiteConstants.objects.count() == 0:
            return redirect('/installation/')
        obj=SiteConstants.objects.all()[0]
        form=users_registerForm()
        eform=EProfileForm()
        data={
            'title':'Add new employee',
            'obj':obj,
            'data':request.user,
            'form':form,
            'eform':eform
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
            'edit':True
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