from django import forms
from choices import COUNTRY_CHOICES
from captcha.fields import CaptchaField
from nepi.main.models import Country, Course, School, UserProfile


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
    country = forms.ChoiceField(required=True,
                                label="What country do you reside in?",
                                choices=COUNTRY_CHOICES)
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

'''Do I really need three forms or is their
a better way to do this dynamically?'''


class CountryCourseForm(forms.Form):
    country = forms.ChoiceField(required=True,
                                label="What country do you reside in?",
                                choices=COUNTRY_CHOICES)
    school = forms.ModelChoiceField(queryset=Country.objects.all())


class SchoolCourseForm(forms.Form):
    country = forms.ChoiceField(required=True,
                                label="What country do you reside in?",
                                choices=COUNTRY_CHOICES)
    school = forms.ModelChoiceField(queryset=Country.objects.all())
    course = forms.ModelChoiceField(queryset=Course.objects.all())


class ContactForm(forms.Form):
    '''This is a form class that will be returned
    later in the contact form view.'''
    sender = forms.EmailField(required=True)
    subject = forms.CharField(max_length=100, required=True)
    message = forms.CharField(max_length=500, required=True,
                              widget=forms.Textarea)
    captcha = CaptchaField()


class ICAPForm(forms.Form):
    countries = forms.ModelChoiceField(queryset=Country.objects.all())
    schools = forms.ModelChoiceField(queryset=School.objects.all())
    groups = forms.ModelChoiceField(queryset=Course.objects.all())


class UpdateProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True,
                                 label="First Name")
    last_name = forms.CharField(max_length=100, required=True,
                                label="Last Name")
    faculty_access = forms.BooleanField(
        required=False, label="Request Faculty Access")
    email = forms.EmailField(required=False, label="Email(not required):")
    password1 = forms.CharField(max_length=100, required=False,
                                label="Leave blank if you" +
                                "wish to leave the same")
    password2 = forms.CharField(max_length=100, required=False,
                                label="Leave blank if you wish" +
                                "to leave the same")

    def __init__(self, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
        passed_profile = kwargs.get('instance')
        #print passed_profile
        self.fields['first_name'].initial = passed_profile.user.first_name
        self.fields['last_name'].initial = passed_profile.user.last_name
        self.fields['email'].initial = passed_profile.user.email

    class Meta:
        model = UserProfile
        exclude = ['profile_type', 'course', 'school', 'user']

    def clean(self):
        form = super(UpdateProfileForm, self).clean()
        faculty_access = form.get("faculty_access")
        email = form.get("email")
        password1 = form.get("password1")
        password2 = form.get("password2")

        if faculty_access and (email == ""):
            self._errors["email"] = self.error_class(
                ["If you are registering as an instructor " +
                 "you must enter a valid email address"])
        if password1 != password2:
            self._errors["password1"] = self.error_class(
                ["Passwords must match each other."])
            self._errors["password2"] = self.error_class(
                ["Passwords must match each other."])
        return form

    def save(self, *args, **kwargs):
        '''to save attributes from another model must explicitly save the extra fields of the form'''
        self.instance.user.first_name = self.cleaned_data.get('first_name')
        self.instance.user.last_name = self.cleaned_data.get('last_name')
        self.instance.user.email = self.cleaned_data.get('email')
        if self.cleaned_data.get('password1') and self.cleaned_data.get('password2'):
            self.instance.user.last_name = self.cleaned_data.get('password1')
        self.instance.user.save()
        return super(UpdateProfileForm, self).save(*args, **kwargs)




class CreateCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        exclude = ("school", "creator")
