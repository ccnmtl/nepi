from django import forms
from choices import COUNTRY_CHOICES
from captcha.fields import CaptchaField
from nepi.main.models import Country, School, Course


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, required=True)
    password = forms.CharField(widget=forms.PasswordInput,
                               max_length=50,
                               required=True)

    def form_valid(self, form):
        pass


class CreateAccountForm(forms.Form):
    '''This is a form class that will be used
    to allow guest users to create guest accounts.'''

    first_name = forms.CharField(
        max_length=25, required=True, label="First Name")
    last_name = forms.CharField(
        max_length=25, required=True, label="Last Name")
    username = forms.CharField(
        max_length=25, required=True, label="Username")
    email = forms.EmailField(required=False, label="Email(not required):")
    country = forms.ChoiceField(required=True, label="What country do you reside in?", choices=COUNTRY_CHOICES)
    nepi_affiliated = forms.BooleanField(required=False)
    password1 = forms.CharField(
        max_length=25, widget=forms.PasswordInput, required=True,
        label="Password")
    password2 = forms.CharField(
        max_length=25, widget=forms.PasswordInput, required=True,
        label="Confirm Password")
    profile_type = forms.BooleanField(
        required=False, label="Are you a Teacher?")
    captcha = CaptchaField()

    def clean(self):
        form = super(CreateAccountForm, self).clean()
        is_teacher = form.get("profile_type")
        email = form.get("email")
        password1 = form.get("password1")
        password2 = form.get("password2")

        if is_teacher and (email == ""):
            self._errors["email"] = self.error_class(
                ["If you are registering as an instructor " +
                 "you must enter a valid email address"])
        if password1 != password2:
            self._errors["password1"] = self.error_class(
                ["Passwords must match each other."])
            self._errors["password2"] = self.error_class(
                ["Passwords must match each other."])
        return form

'''Do I really need three forms or is their a better way to do this dynamically?'''
class CountryCourseForm(forms.Form):
    country = forms.ChoiceField(required=True, label="What country do you reside in?", choices=COUNTRY_CHOICES)
    school = forms.ModelChoiceField(queryset=Country.objects.all())

class SchoolCourseForm(forms.Form):
    country = forms.ChoiceField(required=True, label="What country do you reside in?", choices=COUNTRY_CHOICES)
    school = forms.ModelChoiceField(queryset=Country.objects.all())
#    course = forms.ModelChoiceField(queryset=Course.objects.all())



class ContactForm(forms.Form):
    '''This is a form class that will be returned
    later in the contact form view.'''
    sender = forms.EmailField(required=True)
    subject = forms.CharField(max_length=100, required=True)
    message = forms.CharField(max_length=500, required=True,
                              widget=forms.Textarea)
