from django import forms
from captcha.fields import CaptchaField


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, required=True)
    password = forms.CharField(widget=forms.PasswordInput,
                               max_length=50,
                               required=True)

    def form_valid(self, form):
        form_data = form.cleaned_data


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
    profile_type = forms.BooleanField(
        required=False, label="Are you a Teacher?")
    captcha = CaptchaField()

    def clean(self):
        form = super(CreateAccountForm, self).clean()
        is_teacher = form.get("profile_type")
        email = form.get("email")
        password1 = form.get("password1")
        password2 = form.get("password2")
        f_username = form.get("username")

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


class ContactForm(forms.Form):
    '''This is a form class that will be returned
    later in the contact form view.'''
    sender = forms.EmailField(required=True)
    subject = forms.CharField(max_length=100, required=True)
    message = forms.CharField(max_length=500, required=True,
                              widget=forms.Textarea)
