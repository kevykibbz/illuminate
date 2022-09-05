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
from installation.forms import SiteConstants
from django.contrib.auth import authenticate
import re
from urllib.parse import urlparse


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
    name=forms.CharField(widget=forms.TextInput(attrs={'aria-required':'true','class':'form-control  input-sm input-round','placeholder':'Full name','aria-label':'name'}),error_messages={'required':'Full name is required'})
    phone=PhoneNumberField(widget=PhoneNumberPrefixWidget(attrs={'aria-required':'true','class':'form-control  input-sm input-round','type':'tel','aria-label':'phone','placeholder':'Phone'},initial="KE"),error_messages={'required':'Phone number is required'})
    email=forms.EmailField(widget=forms.EmailInput(attrs={'aria-required':'true','class':'form-control  input-sm input-round','placeholder':'Email address','aria-label':'email'}),error_messages={'required':'Email address is required'})
    subject=forms.CharField(widget=forms.TextInput(attrs={'aria-required':'true','class':'form-control  input-sm input-round','placeholder':'subject ','aria-label':'subject'}),error_messages={'required':'Subject is required'})
    message=forms.CharField(widget=forms.Textarea(attrs={'rows':5,'aria-required':'true','class':'form-control  input-sm','placeholder':'Message','aria-label':'message'}),error_messages={'required':'Message is required','min_length':'enter atleast 6 characters long'})

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

class UsersReplyForm(forms.ModelForm):
    reply=forms.CharField(widget=forms.Textarea(attrs={'rows':5,'cols':30,'aria-required':'true','class':'form-control  input-sm w-100','placeholder':'Message','aria-label':'reply'}),error_messages={'required':'Feedback is required','min_length':'enter atleast 6 characters long'})

    class Meta:
        model=ContactModel
        fields=['reply',]





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
    oldpassword=forms.CharField(widget=forms.PasswordInput(attrs={'aria-required':'true','class':'form-control input-rounded','placeholder':'Old password','aria-label':'oldpassword'}),error_messages={'required':'Old password is required','min_length':'enter atleast 6 characters long'})
    password1=forms.CharField(widget=forms.PasswordInput(attrs={'aria-required':'true','class':'form-control input-rounded','placeholder':'New password Eg Example12','aria-label':'password1'}),error_messages={'required':'New password is required','min_length':'enter atleast 6 characters long'})
    password2=forms.CharField(widget=forms.PasswordInput(attrs={'aria-required':'true','class':'form-control input-rounded','placeholder':'Confirm new password','aria-label':'password2'}),error_messages={'required':'Confirm new password is required'})

    class Meta:
        model=User
        fields=['password1','password2']
    
    def clean_oldpassword(self):
        oldpassword=self.cleaned_data['oldpassword']
        if not self.instance.check_password(oldpassword):
            raise forms.ValidationError('Wrong old password.')
        else:
           return oldpassword 

#profileForm
class CurrentLoggedInUserProfileChangeForm(UserChangeForm):
    first_name=forms.CharField(widget=forms.TextInput(attrs={'style':'text-transform:lowercase;','class':'form-control input-rounded'}),required=False)
    last_name=forms.CharField(widget=forms.TextInput(attrs={'style':'text-transform:lowercase;','class':'form-control input-rounded','aria-label':'last_name'}),error_messages={'required':'Last name is required'})
    username=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control input-rounded','placeholder':'Username ','aria-label':'username'}),error_messages={'required':'Username is required'})
    email=forms.EmailField(widget=forms.EmailInput(attrs={'style':'text-transform:lowercase;','class':'form-control input-rounded','aria-label':'email'}),error_messages={'required':'Email address is required'})
    is_active=forms.BooleanField(widget=forms.CheckboxInput(attrs={'aria-label':'is_active','id':'checkbox1'}),required=False)
    class Meta:
        model=User
        fields=['first_name','last_name','email','is_active','username',]


    def clean_first_name(self):
        first_name=self.cleaned_data['first_name']
        if not str(first_name).isalpha():
                raise forms.ValidationError('only characters are allowed.')
        return first_name
    
    def clean_last_name(self):
        last_name=self.cleaned_data['last_name']
        if not str(last_name).isalpha():
                raise forms.ValidationError('only characters are allowed.')
        return last_name

    def clean_email(self):
        email=self.cleaned_data['email']
        if email != self.instance.email:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('A user with this email already exists.')
            try:
                validate_email(email)
            except ValidationError as e:
                raise forms.ValidationError('Invalid email address.')
            return email
        else:
           return email

    def clean_username(self):
        username=self.cleaned_data['username']
        if email != self.instance.email:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('A user with this username already exists')
            return username
        return username

options=[
            ('employee','Employee'),
            ('admins','Admin'),
        ]

#profileForm
class CurrentExtUserProfileChangeForm(forms.ModelForm):
    phone=PhoneNumberField(widget=PhoneNumberPrefixWidget(attrs={'class':'form-control input-rounded','type':'tel','aria-label':'phone','placeholder':'Phone example +25479626...'}),error_messages={'required':'Phone number is required'})
    role=forms.ChoiceField(choices=options,initial="Tertiary", error_messages={'required':'Role is required','aria-label':'role'},
    widget=forms.Select(attrs={'class':'form-control input-rounded','placeholder':'Role'}))
    bio=forms.CharField(widget=forms.Textarea(attrs={'style':'text-transform:lowercase;','class':'form-control','aria-label':'email'}),required=False)
    profile_pic=forms.ImageField(
                                widget=forms.FileInput(attrs={'class':'profile','accept':'image/*','hidden':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','gif'],message="Invalid image extension",code="invalid_extension")]
                                )
    class Meta:
        model=ExtendedAuthUser
        fields=['phone','profile_pic','bio',]

    
    def clean_phone(self):
        phone=self.cleaned_data['phone']
        if phone != self.instance.phone:
            if ExtendedAuthUser.objects.filter(phone=phone).exists():
                raise forms.ValidationError('A user with this phone number already exists.')
            else:
                return phone
        else:
           return phone 

class users_registerForm(UserCreationForm):
    first_name=forms.CharField(widget=forms.TextInput(attrs={'class':'fname form-control input-rounded','placeholder':'First name','aria-label':'first_name'}),error_messages={'required':'First name is required'})
    last_name=forms.CharField(widget=forms.TextInput(attrs={'class':'lname form-control input-rounded','placeholder':'Last name','aria-label':'last_name'}),error_messages={'required':'Last name is required'})
    email=forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control input-rounded','placeholder':'Email address','aria-label':'email'}),error_messages={'required':'Email address is required'})
    username=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control input-rounded','placeholder':'Username ','aria-label':'username'}),error_messages={'required':'Username is required'})
    password1=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control input-rounded','placeholder':'Password Eg Example12','aria-label':'password1'}),error_messages={'required':'Password is required','min_length':'enter atleast 6 characters long'})
    password2=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control input-rounded','placeholder':'Confirm password','aria-label':'password2'}),error_messages={'required':'Confirm password is required'})

    class Meta:
        model=User
        fields=['first_name','last_name','email','username','password1','password2']


    def clean_first_name(self):
        first_name=self.cleaned_data['first_name']
        if not str(first_name).isalpha():
                raise forms.ValidationError('only characters are allowed')
        return first_name
    
    def clean_last_name(self):
        last_name=self.cleaned_data['last_name']
        if not str(last_name).isalpha():
                raise forms.ValidationError('only characters are allowed')
        return last_name
           

    def clean_email(self):
        email=self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists')
        try:
            validate_email(email)
        except ValidationError as e:
            raise forms.ValidationError('invalid email address')
        return email
    
    def clean_username(self):
        username=self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('A user with this username already exists')
        return username
options=[
            ('employee','Employee'),
            ('admins','Admin'),
        ]
class EProfileForm(forms.ModelForm):
    phone=PhoneNumberField(widget=PhoneNumberPrefixWidget(attrs={'class':'form-control input-rounded','type':'tel','aria-label':'phone','placeholder':'Phone'}),error_messages={'required':'Phone number is required'})
    role=forms.ChoiceField(required=False,choices=options,initial="Tertiary",widget=forms.Select(attrs={'class':'form-control input-rounded','placeholder':'Role'}))
    profile_pic=forms.ImageField(
                                widget=forms.FileInput(attrs={'class':'profile','accept':'image/*','hidden':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','gif'],message="Invalid image extension",code="invalid_extension")]
                                )
    class Meta:
        model=ExtendedAuthUser
        fields=['phone','role','profile_pic']

    
    def clean_phone(self):
        phone=self.cleaned_data['phone']
        if phone !='':
            if ExtendedAuthUser.objects.filter(phone=phone).exists():
                raise forms.ValidationError('A user with this phone number already exists.')
            else:
                return phone
        else:
            raise forms.ValidationError('Phone number is required')

class ProfilePicForm(forms.ModelForm):
    profile_pic=forms.ImageField(
                                widget=forms.FileInput(attrs={'class':'profile','accept':'image/*','hidden':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','gif'],message="Invalid image extension",code="invalid_extension")]
                                )
    class Meta:
        model=ExtendedAuthUser
        fields=['profile_pic',]

class SiteForm(forms.ModelForm):
    site_name=forms.CharField(widget=forms.EmailInput(attrs={'aria-label':'site_name','class':'form-control input-rounded','placeholder':'Site name'}),error_messages={'required':'Site Name is required'})
    description=forms.CharField(widget=forms.Textarea(attrs={'aria-label':'description','class':'form-control','placeholder':'Site Description'}),error_messages={'required':'Site Description is required'})
    theme_color=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'theme_color','class':'form-control gradient-colorpicker input-rounded','placeholder':'Site Theme Color eg #ff0000'}),required=False)
    key_words=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'key_words','class':'form-control input-rounded tags','placeholder':'Site Keywords'}),required=False)
    site_url=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'site_url','class':'form-control input-rounded','placeholder':'Site URL'}),error_messages={'required':'Site URL is required'})
    favicon=forms.ImageField(
                                widget=forms.FileInput(attrs={'aria-label':'favicon','class':'custom-file-input','id':'customFileInput','accept':'image/*','hidden':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','ico'],message="Invalid image extension",code="invalid_extension")]
                                )
    class Meta:
        model=SiteConstants
        fields=['site_name','theme_color','site_url','description','key_words','favicon',]
    
    def clean_theme_color(self):
        theme_color=self.cleaned_data['theme_color']
        match=re.search(r'^#(?:[0-9a-fA-F]{1,2}){3}$',theme_color)
        if not match:
            raise forms.ValidationError('Invalid color code given')
        else:
            return theme_color
            
    def clean_site_url(self):
        site_url=self.cleaned_data['site_url']
        if URLValidator(site_url):
            return site_url
        else:
            raise forms.ValidationError('Invalid url')

#AddressConfigForm
class AddressConfigForm(forms.ModelForm):
    site_email=forms.EmailField(widget=forms.EmailInput(attrs={'aria-label':'site_email','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Site Email Address'}),error_messages={'required':'Address is required'})
    site_email2=forms.EmailField(widget=forms.EmailInput(attrs={'aria-label':'site_email2','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Site Additional Email Address'}),required=False)
    address=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'address','style':'text-transform:lowercase;','class':'form-control input-rounded'}),error_messages={'required':'Address is required'})
    location=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'location','style':'text-transform:lowercase;','class':'form-control input-rounded'}),error_messages={'required':'Location is required'})
    phone=PhoneNumberField(widget=PhoneNumberPrefixWidget(attrs={'aria-label':'phone','style':'text-transform:lowercase;','class':'form-control input-rounded'},initial='KE'),required=False)
    class Meta:
        model=SiteConstants
        fields=['address','location','phone','site_email','site_email2']
    
    def clean_site_email(self):
        email=self.cleaned_data['site_email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        try:
            validate_email(email)
        except ValidationError as e:
            raise forms.ValidationError('Invalid email address.')
        return email
    
    def clean_site_email2(self):
        email=self.cleaned_data['site_email2']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        try:
            validate_email(email)
        except ValidationError as e:
            raise forms.ValidationError('Invalid email address.')
        return email


#social form
class UserSocialForm(forms.ModelForm):
    facebook=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'facebook','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Facebook Link'}),required=False)    
    twitter=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'twitter','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Twitter Link'}),required=False)    
    github=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'github','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Github Link'}),required=False)  
    instagram=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'instagram','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Instagram Link'}),required=False)    
    linkedin=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'linkedin','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Linkedin Link'}),required=False)   
    youtube=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'youtube','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Youtube Link'}),required=False)    
    whatsapp=forms.URLField(widget=forms.URLInput(attrs={'aria-label':'whatsapp','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Whats App'}),required=False)
    class Meta:
        model=SiteConstants
        fields=['facebook','twitter','linkedin','instagram','whatsapp','youtube','github',]

    def clean_facebook(self):
        facebook=self.cleaned_data['facebook']
        if URLValidator(facebook):
                output=urlparse(facebook)
                username=output.path.strip('/')
                if not username:
                    raise forms.ValidationError('Username parameter missing')
                else:
                    return [facebook,username]
        else:
            raise forms.ValidationError('Invalid url')
    
    def clean_twitter(self):
        twitter=self.cleaned_data['twitter']
        if URLValidator(twitter):
                output=urlparse(twitter)
                username=output.path.strip('/')
                if not username:
                    raise forms.ValidationError('Username parameter missing')
                else:
                    return [twitter,username]
        else:
            raise forms.ValidationError('Invalid url')
    

    def clean_github(self):
        github=self.cleaned_data['github']
        if URLValidator(github):
                output=urlparse(github)
                username=output.path.strip('/')
                if not username:
                    raise forms.ValidationError('Username parameter missing')
                else:
                    return [github,username]
        else:
            raise forms.ValidationError('Invalid url')
    def clean_instagram(self):
        instagram=self.cleaned_data['instagram']
        if URLValidator(instagram):
                output=urlparse(instagram)
                username=output.path.strip('/')
                if not username:
                    raise forms.ValidationError('Username parameter missing')
                else:
                    return [instagram,username]
        else:
            raise forms.ValidationError('Invalid url')
    
    def clean_linkedin(self):
        linkedin=self.cleaned_data['linkedin']
        if URLValidator(linkedin):
                output=urlparse(linkedin)
                username=output.path.strip('/')
                if not username:
                    raise forms.ValidationError('Username parameter missing')
                else:
                    return [linkedin,username]
        else:
            raise forms.ValidationError('Invalid url')
    
    def clean_youtube(self):
        youtube=self.cleaned_data['youtube']
        if URLValidator(youtube):
                output=urlparse(youtube)
                username=output.path.strip('/')
                if not username:
                    raise forms.ValidationError('Channel id parameter missing')
                else:
                    return [youtube,username]
        else:
            raise forms.ValidationError('Invalid url')
    def clean_whatsapp(self):
        whatsapp=self.cleaned_data['whatsapp']
        if URLValidator(whatsapp):
            output=urlparse(whatsapp)
            username=output.path.strip('/')
            if not username:
                raise forms.ValidationError('username parameter missing')
            else:
                return [whatsapp,username]
        else:
            raise forms.ValidationError('Invalid url')

#WorkingConfigForm
class WorkingConfigForm(forms.ModelForm):
    working_days=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'working_days','style':'text-transform:lowercase;','class':'form-control input-rounded'}),error_messages={'required':'Working days is required'})
    working_hours=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'working_hours','style':'text-transform:lowercase;','class':'form-control input-rounded'}),error_messages={'required':'Working hours is required'})

    class Meta:
        model=SiteConstants
        fields=['working_days','working_hours',]

class CategoryForm(forms.ModelForm):
    category=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'category','class':'form-control input-rounded','placeholder':'Enter category name'}),error_messages={'required':'Category name is required'})

    class Meta:
        model=CategoryModel
        fields=['category',]

class GallaryForm(forms.ModelForm):
    category=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'category','class':'form-control input-rounded','placeholder':'Enter category name'}),error_messages={'required':'Category name is required'})
    imagegallary=forms.ImageField(
                                widget=forms.FileInput(attrs={'class':'dropify','data-default-file':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','gif'],message="Invalid image extension",code="invalid_extension")]
                                )
    class Meta:
        model=GallaryModel
        fields=['category','imagegallary',]


#ServiceForm
class ServiceForm(forms.ModelForm):
    title=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'title','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Title'}),error_messages={'required':'Title is required'})
    description=forms.CharField(widget=forms.Textarea(attrs={'aria-label':'description','style':'text-transform:lowercase;','class':'form-control','placeholder':'Description'}),error_messages={'required':'Description is required'})
    total=forms.CharField(widget=forms.NumberInput(attrs={'aria-label':'total','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Total money to be raised'}),error_messages={'required':'Total money to be raised is required'})
    raised=forms.CharField(widget=forms.NumberInput(attrs={'aria-label':'raised','style':'text-transform:lowercase;','class':'form-control input-rounded','placeholder':'Total money raised'}),required=False)
    imagegallary=forms.ImageField(
                                widget=forms.FileInput(attrs={'class':'dropify','data-default-file':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','gif'],message="Invalid image extension",code="invalid_extension")]
                                )
    class Meta:
        model=ServiceModel
        fields=['title','description','total','raised','imagegallary',]

#AboutForm
class AboutForm(forms.ModelForm):
    h1=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'h1','class':'form-control input-rounded'}),required=False)
    h1_text=forms.CharField(widget=forms.Textarea(attrs={'aria-label':'h1_text','class':'form-control'}),required=False)  
    h2=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'h2','class':'form-control input-rounded'}),required=False)
    h2_text=forms.CharField(widget=forms.Textarea(attrs={'aria-label':'h2_text','class':'form-control'}),required=False)
    h2_image=forms.ImageField(
                                widget=forms.FileInput(attrs={'aria-label':'h2_image','class':'dropify','data-default-file':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','gif'],message="Invalid image extension",code="invalid_extension")]
                                )
    h3=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'h3','class':'form-control input-rounded'}),required=False)
    h3_text=forms.CharField(widget=forms.Textarea(attrs={'aria-label':'h3_text','class':'form-control'}),required=False)
    h3_image=forms.ImageField(
                                widget=forms.FileInput(attrs={'aria-label':'h3_image','class':'dropify','data-default-file':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','gif'],message="Invalid image extension",code="invalid_extension")]
                                )
    class Meta:
        model=AboutModel
        fields=['h1','h1_text','h2','h2_text','h2_image','h3','h3_text','h3_image',]


class HomeForm(forms.ModelForm):
    slider1_head=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'slider1_head','class':'form-control input-rounded'}),required=False)
    slider1_text=forms.CharField(widget=forms.Textarea(attrs={'aria-label':'slider1_text','class':'form-control'}),required=False)
    slider1_image=forms.ImageField(widget=forms.FileInput(attrs={'aria-label':'slider1_image','class':'dropify','data-default-file':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','gif'],message="Invalid image extension",code="invalid_extension")]
                                )
    slider2_head=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'slider2_head','class':'form-control input-rounded'}),required=False)
    slider2_text=forms.CharField(widget=forms.Textarea(attrs={'aria-label':'slider2_text','class':'form-control'}),required=False)
    slider2_image=forms.ImageField(widget=forms.FileInput(attrs={'aria-label':'slider1_image','class':'dropify','data-default-file':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','gif'],message="Invalid image extension",code="invalid_extension")]
                                )
    slider3_head=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'slider3_head','class':'form-control input-rounded'}),required=False)
    slider3_text=forms.CharField(widget=forms.Textarea(attrs={'aria-label':'slider3_text','class':'form-control'}),required=False)
    slider3_image=forms.ImageField(widget=forms.FileInput(attrs={'aria-label':'slider3_image','class':'dropify','data-default-file':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','gif'],message="Invalid image extension",code="invalid_extension")]
                                )
    service_head=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'service_head','class':'form-control input-rounded'}),required=False)
    service_text=forms.CharField(widget=forms.Textarea(attrs={'aria-label':'service_text','class':'form-control'}),required=False) 
    archieve_head=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'archieve_head','class':'form-control input-rounded'}),required=False)
    archieve_text=forms.CharField(widget=forms.Textarea(attrs={'aria-label':'archieve_text','class':'form-control'}),required=False)
    archieve_bg=forms.ImageField(widget=forms.FileInput(attrs={'aria-label':'archieve_bg','class':'dropify','data-default-file':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','gif'],message="Invalid image extension",code="invalid_extension")]
                                )
    no_year_of_expe=forms.CharField(widget=forms.NumberInput(attrs={'aria-label':'no_year_of_expe','class':'form-control input-rounded'}),initial=0,required=False)
    text_year_of_expe=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'text_year_of_expe','class':'form-control input-rounded'}),required=False) 
    no_happy_children=forms.CharField(widget=forms.NumberInput(attrs={'aria-label':'no_happy_children','class':'form-control input-rounded'}),initial=0,required=False)
    text_happy_children=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'text_happy_children','class':'form-control input-rounded'}),required=False)
    no_event=forms.CharField(widget=forms.NumberInput(attrs={'aria-label':'no_event','class':'form-control input-rounded'}),initial=0,required=False)
    text_event=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'text_event','class':'form-control input-rounded'}),required=False) 
    no_fund_raised=forms.IntegerField(widget=forms.NumberInput(attrs={'aria-label':'no_fund_raised','class':'form-control input-rounded'}),initial=0,required=False)
    text_fund_raised=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'text_fund_raised','class':'form-control input-rounded'}),required=False)
    team_head=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'team_head','class':'form-control input-rounded'}),required=False)
    team1_name=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'team1_name','class':'form-control input-rounded'}),required=False)
    team1_title=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'team1_title','class':'form-control input-rounded'}),required=False)
    team1_image=forms.ImageField(widget=forms.FileInput(attrs={'aria-label':'team1_image','class':'dropify','data-default-file':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','gif'],message="Invalid image extension",code="invalid_extension")]
                                )
    team2_name=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'team2_name','class':'form-control input-rounded'}),required=False)
    team2_title=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'team2_title','class':'form-control input-rounded'}),required=False)
    team2_image=forms.ImageField(widget=forms.FileInput(attrs={'aria-label':'team2_image','class':'dropify','data-default-file':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','gif'],message="Invalid image extension",code="invalid_extension")]
                                )
    team3_name=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'team3_name','class':'form-control input-rounded'}),required=False)
    team3_title=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'team3_title','class':'form-control input-rounded'}),required=False)
    team3_image=forms.ImageField(widget=forms.FileInput(attrs={'aria-label':'team3_image','class':'dropify','data-default-file':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','gif'],message="Invalid image extension",code="invalid_extension")]
                                )
    team4_name=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'team4_name','class':'form-control input-rounded'}),required=False)
    team4_title=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'team4_title','class':'form-control input-rounded'}),required=False)
    team4_image=forms.ImageField(widget=forms.FileInput(attrs={'aria-label':'team4_image','class':'dropify','data-default-file':True}),
                                required=False,
                                validators=[FileExtensionValidator(['jpg','jpeg','png','gif'],message="Invalid image extension",code="invalid_extension")]
                                )
    class Meta:
        model=HomeModel
        fields=['slider1_head','slider1_text','slider1_image','slider2_head','team_head',
        'slider2_text','slider2_image','slider3_head','slider3_text','slider3_image','service_head','service_text','archieve_head',
        'archieve_text','archieve_bg','no_year_of_expe','text_year_of_expe','no_happy_children','text_happy_children','no_event',
        'text_event','no_fund_raised','text_fund_raised','team1_name','team1_title','team1_image','team2_name','team2_title','team2_image',
        'team3_name','team3_title','team3_image','team4_name','team4_title','team4_image',
        ]

class SliderForm(forms.ModelForm):
    slider_head=forms.CharField(widget=forms.TextInput(attrs={'aria-label':'slider_head','class':'form-control input-rounded'}))
    slider_text=forms.CharField(widget=forms.Textarea(attrs={'aria-label':'slider_text','class':'form-control'}))
    slider_image=forms.ImageField(widget=forms.FileInput(attrs={'aria-label':'slider_image','class':'dropify','data-default-file':True}),
                                validators=[FileExtensionValidator(['jpg','jpeg','png','gif'],message="Invalid image extension",code="invalid_extension")]
                                )
    class Meta:
        model=SliderModel
        fields=['slider_head','slider_text','slider_image',]