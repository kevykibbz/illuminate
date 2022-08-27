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
import os
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