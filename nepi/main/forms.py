from captcha.fields import CaptchaField
from choices import COUNTRY_CHOICES
from django import forms
from django.contrib.auth.models import User
from django.forms.fields import ChoiceField


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, required=True)
    password = forms.CharField(widget=forms.PasswordInput,
                               max_length=50,
                               required=True)

    def form_valid(self, form):
        pass


class ChoiceFieldNoValidation(ChoiceField):
    def validate(self, value):
        return True


class CreateAccountForm(forms.Form):
    '''This is a form class that will be used
    to allow guest users to create guest accounts.'''

    first_name = forms.CharField(
        max_length=50, required=True)
    last_name = forms.CharField(
        max_length=50, required=True)
    username = forms.CharField(
        max_length=25, required=True)
    email = forms.EmailField(required=False)
    country = forms.ChoiceField(required=True, choices=COUNTRY_CHOICES)

    # School is not validated as it is variably required
    # Yes for teachers, No for students
    school = ChoiceFieldNoValidation(required=False)

    nepi_affiliated = forms.BooleanField(required=False)
    password1 = forms.CharField(
        max_length=25, widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(
        max_length=25, widget=forms.PasswordInput, required=True)
    profile_type = forms.BooleanField(required=False)
    captcha = CaptchaField()

    def clean(self):
        form = super(CreateAccountForm, self).clean()
        is_teacher = form.get("profile_type")
        username = form.get("username")
        email = form.get("email")
        school = form.get("school")
        password1 = form.get("password1")
        password2 = form.get("password2")
        country = form.get("country")

        if User.objects.filter(username=username).count() > 0:
            self._errors["username"] = self.error_class(
                ["This username is taken. Please select a different one"])

        if is_teacher:
            if email is None or email == "":
                self._errors["email"] = self.error_class(
                    ["If you are registering as an instructor " +
                     "you must enter a valid email address"])
            if school is None or school == "" or school == "-----":
                self._errors["school"] = self.error_class(
                    ["If you are registering as an instructor " +
                     "you must select a school"])

        if password1 != password2:
            self._errors["password1"] = self.error_class(
                ["Passwords must match each other."])
            self._errors["password2"] = self.error_class(
                ["Passwords must match each other."])

        if country is None or country == '-----':
            self._errors['country'] = self.error_class([
                "This field is required"])

        return form


class ContactForm(forms.Form):
    '''This is a form class that will be returned
    later in the contact form view.'''
    first_name = forms.CharField(
        max_length=50, required=True)
    last_name = forms.CharField(
        max_length=50, required=True)
    sender = forms.EmailField(required=True, label="Your email is:")
    subject = forms.CharField(max_length=100, required=True)
    message = forms.CharField(max_length=1024, required=True,
                              widget=forms.Textarea)
    captcha = CaptchaField()


class UpdateProfileForm(forms.Form):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=False)
    profile_type = forms.BooleanField(required=False)
    country = forms.ChoiceField(required=True, choices=COUNTRY_CHOICES)

    # School is not validated as it is variably required
    # Yes for teachers, No for students. Same for email
    school = ChoiceFieldNoValidation(required=False)

    password1 = forms.CharField(max_length=100, required=False)
    password2 = forms.CharField(max_length=100, required=False)

    nepi_affiliated = forms.BooleanField(required=False)

    def clean(self):
        form = super(UpdateProfileForm, self).clean()
        is_teacher = form.get("profile_type")
        email = form.get("email")
        school = form.get("school")
        password1 = form.get("password1")
        password2 = form.get("password2")
        country = form.get("country")

        if is_teacher:
            if email is None or email == "":
                self._errors["email"] = self.error_class(
                    ["If you are registering as an instructor " +
                     "you must enter a valid email address"])
            if school is None or school == "" or school == "-----":
                self._errors["school"] = self.error_class(
                    ["If you are registering as an instructor " +
                     "you must select a school"])

        if password1 != password2:
            self._errors["password1"] = self.error_class(
                ["Passwords must match each other."])
            self._errors["password2"] = self.error_class(
                ["Passwords must match each other."])

        if country is None or country == '-----':
            self._errors['country'] = self.error_class([
                "This field is required"])

        return form
