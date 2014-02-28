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
    email = forms.EmailField(required=False)
    #country = forms.ChoiceField(choices=COUNTRY_CHOICES, required=False)
    profile_type = forms.BooleanField(required=False, label="Are you a Teacher?")
    #captcha = CaptchaField()

    def clean(self):
        form = super(CreateAccountForm, self).clean()
        is_teacher = form.get("profile_type")
        email = form.get("email")
        password1 = form.get("password1")
        password2 = form.get("password2")
        f_username = form.get("username")

        if is_teacher and (email == ""):
            self._errors["email"] = self.error_class(["If you are registering as an instructor you must enter a valid email address"])
            #raise forms.ValidationError("If you are registering as an instructor you must enter a valid email address")
        if password1 != password2:
            self._errors["password1"] = self.error_class(["Passwords must match each other."])
            self._errors["password2"] = self.error_class(["Passwords must match each other."])
            #raise forms.ValidationError("passwords dont match each other")
#        try:
#            User.objects.get(username=f_username)
#            self._errors["username"] = self.error_class(["This username is taken, please pick another one."])
            #raise forms.ValidationError("this username already exists")
#        except:
#            pass

        return form


class ContactForm(forms.Form):
    '''This is a form class that will be returned
    later in the contact form view.'''
    sender = forms.EmailField(required=True)
    subject = forms.CharField(max_length=100, required=True)
    message = forms.CharField(max_length=500, required=True,
                              widget=forms.Textarea)


class AddTeacher(forms.Form):
    pass


class AddSchoolForm(forms.Form):
    name = forms.CharField(max_length=50, required=True, label="School Name")
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, required=True)


class CaptchaTestForm(forms.Form):
    captcha = CaptchaField()


class AjaxForm(forms.Form):
    captcha = CaptchaField()
