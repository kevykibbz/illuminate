from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import *
from django import forms
from django.contrib.auth.forms import PasswordResetForm, UserCreationForm,UserChangeForm,PasswordChangeForm
from django.contrib.auth.forms import User
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django.contrib.auth.hashers import check_password
from django.core.validators import FileExtensionValidator,URLValidator
from installation.models import SiteConstants
from django.contrib.auth import authenticate

class UserResetPassword(PasswordResetForm):
    email=forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Enter email address'}),error_messages={'required':'Email address is required'})

    def clean_email(self):
        email=self.cleaned_data['email']
        if  not User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email address does not exist')
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError('Invalid email address')
        return email


class UsersContactForm(forms.ModelForm):
    name=forms.CharField(widget=forms.TextInput(attrs={'aria-required':'true','class':'form-control','placeholder':'Full name','aria-label':'name'}),error_messages={'required':'Full name is required'})
    phone=PhoneNumberField(widget=PhoneNumberPrefixWidget(attrs={'aria-required':'true','class':'form-control','type':'tel','aria-label':'phone','placeholder':'Phone'},initial="IN"),error_messages={'required':'Phone number is required'})
    email=forms.EmailField(widget=forms.EmailInput(attrs={'aria-required':'true','class':'form-control','placeholder':'Email address','aria-label':'email'}),error_messages={'required':'Email address is required'})
    subject=forms.CharField(widget=forms.TextInput(attrs={'aria-required':'true','class':'form-control','placeholder':'subject ','aria-label':'subject'}),error_messages={'required':'Subject is required'})
    message=forms.CharField(widget=forms.Textarea(attrs={'rows':5,'aria-required':'true','class':'form-control','placeholder':'Message','aria-label':'message'}),error_messages={'required':'Message is required','min_length':'enter atleast 6 characters long'})

    class Meta:
        model=ContactModel
        fields=['name','phone','email','subject','message',]


    def clean_name(self):
        name=self.cleaned_data['name']
        if len(name.split(" ")) > 1:
            first_name=name.split(" ")[0]
            last_name=name.split(" ")[1]
            if not str(first_name).isalpha():
                raise forms.ValidationError('only characters are allowed')
            elif not str(last_name).isalpha():
                raise forms.ValidationError('only characters are allowed')
        return name

           

    def clean_email(self):
        email=self.cleaned_data['email']
        try:
            validate_email(email)
        except ValidationError as e:
            raise forms.ValidationError('invalid email address')
        return email




class UserLoginForm(forms.Form):
    username=forms.CharField(widget=forms.TextInput(attrs={'aria-required':'true','class':'form-control','placeholder':'Username ','aria-label':'username'}),error_messages={'required':'Username  is required'})
    password=forms.CharField(widget=forms.PasswordInput(attrs={'aria-required':'true','class':'form-control login-password','placeholder':'Password','aria-label':'password'}),error_messages={'required':'Password is required'})

    class Meta:
        model=User
        fields=['username','password',]

    def clean_username(self):
        username=self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            return username
        else:
            raise forms.ValidationError('invalid username')






class UserPasswordChangeForm(UserCreationForm):
    oldpassword=forms.CharField(widget=forms.PasswordInput(attrs={'aria-required':'true','class':'form-control','placeholder':'Old password','aria-label':'oldpassword'}),error_messages={'required':'Old password is required','min_length':'enter atleast 6 characters long'})
    password1=forms.CharField(widget=forms.PasswordInput(attrs={'aria-required':'true','class':'form-control','placeholder':'New password Eg Example12','aria-label':'password1'}),error_messages={'required':'New password is required','min_length':'enter atleast 6 characters long'})
    password2=forms.CharField(widget=forms.PasswordInput(attrs={'aria-required':'true','class':'form-control','placeholder':'Confirm new password','aria-label':'password2'}),error_messages={'required':'Confirm new password is required'})

    class Meta:
        model=User
        fields=['password1','password2']
    
    def clean_oldpassword(self):
        oldpassword=self.cleaned_data['oldpassword']
        if not self.instance.check_password(oldpassword):
            raise forms.ValidationError('Wrong old password.')
        else:
           return oldpassword 