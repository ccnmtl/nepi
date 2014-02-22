from django import forms
from nepi.main.choices import COUNTRY_CHOICES
from captcha.fields import CaptchaField
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.http import HttpResponseRedirect, HttpResponse

class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, required=True)
    password = forms.CharField(widget=forms.PasswordInput,
                               max_length=50,
                               required=True)


class CreateAccountForm(forms.Form):
    '''This is a form class that will be used
    to allow guest users to create guest accounts.'''

    TEACHER_CHOICES = (
        ('TE', 'Teacher'),
        ('ST', 'Student'),
    )

    first_name = forms.CharField(
        max_length=25, required=True, label="First Name")
    last_name = forms.CharField(
        max_length=25, required=True, label="Last Name")
    username = forms.CharField(
        max_length=25, required=True, label="Username")
    password1 = forms.CharField(
        max_length=25, widget=forms.PasswordInput, required=True,
        label="Password")
    password2 = forms.CharField(
        max_length=25, widget=forms.PasswordInput, required=True,
        label="Confirm Password")
    email = forms.EmailField()
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, required=True)
    captcha = CaptchaField()


class ContactForm(forms.Form):
    '''This is a form class that will be returned
    later in the contact form view.'''
    sender = forms.EmailField(required=True)
    subject = forms.CharField(max_length=100, required=True)
    message = forms.CharField(max_length=500, required=True,
                              widget=forms.Textarea)


    def send_email(self):
        pass

class AddTeacher(forms.Form):
    pass


class AddSchoolForm(forms.Form):
    name = forms.CharField(max_length=50, required=True, label="School Name")
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, required=True)


class CaptchaTestForm(forms.Form):
    captcha = CaptchaField()


class AjaxForm(forms.Form):
    captcha = CaptchaField()
