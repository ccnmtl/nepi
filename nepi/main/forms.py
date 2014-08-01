from captcha.fields import CaptchaField
from choices import COUNTRY_CHOICES
from django import forms
from django.forms.fields import ChoiceField
from nepi.main.models import Country, Group, School, UserProfile


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
    school = ChoiceFieldNoValidation(required=False,
                                     label="Please select your school")
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

'''Do I really need three forms or is their
a better way to do this dynamically?'''


class CountryGroupForm(forms.Form):
    country = forms.ChoiceField(required=True,
                                label="What country do you reside in?",
                                choices=COUNTRY_CHOICES)
    school = forms.ModelChoiceField(queryset=Country.objects.all())


class SchoolGroupForm(forms.Form):
    country = forms.ChoiceField(required=True,
                                label="What country do you reside in?",
                                choices=COUNTRY_CHOICES)
    school = forms.ModelChoiceField(queryset=Country.objects.all())
    group = forms.ModelChoiceField(queryset=Group.objects.all())


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


class ICAPForm(forms.Form):
    countries = forms.ModelChoiceField(queryset=Country.objects.all())
    schools = forms.ModelChoiceField(queryset=School.objects.all())
    countrys = forms.ModelChoiceField(queryset=Group.objects.all())


class UpdateProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True,
                                 label="First Name")
    last_name = forms.CharField(max_length=100, required=True,
                                label="Last Name")
    faculty_access = forms.BooleanField(
        required=False, label="Request Faculty Access")
    country = forms.ChoiceField(required=True,
                                label="What country do you reside in?",
                                choices=COUNTRY_CHOICES)
    email = forms.EmailField(required=False, label="Email(not required):")
    password1 = forms.CharField(max_length=100, required=False,
                                label="Password - Leave blank if you" +
                                " wish to leave the same")
    password2 = forms.CharField(max_length=100, required=False,
                                label="Password - Leave blank if you wish" +
                                " to leave the same")

    def __init__(self, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
        passed_profile = kwargs.get('instance')
        #print passed_profile
        self.fields['first_name'].initial = passed_profile.user.first_name
        self.fields['last_name'].initial = passed_profile.user.last_name
        self.fields['email'].initial = passed_profile.user.email
        self.fields['country'].initial = passed_profile.country

    class Meta:
        model = UserProfile
        exclude = ['profile_type', 'group', 'school', 'user']

    def clean(self):
        form = super(UpdateProfileForm, self).clean()
        faculty_access = form.get("faculty_access")
        email = form.get("email")
        password1 = form.get("password1")
        password2 = form.get("password2")
        try:
            new_country = Country.objects.get(name=form.get("country"))
        except Country.DoesNotExist:
            new_country = Country.objects.create(name=form.get("country"))
            new_country.save()
        # country = Country.objects.get(name=form.get("country"))
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
        '''to save attributes from another model must explicitly
        save the extra fields of the form'''
        self.instance.user.first_name = self.cleaned_data.get('first_name')
        self.instance.user.last_name = self.cleaned_data.get('last_name')
        self.instance.user.email = self.cleaned_data.get('email')
        self.instance.user.country = Country.object.get(
            name=self.cleaned_data.get('country'))
        if (self.cleaned_data.get('password1')
                and self.cleaned_data.get('password2')):
            self.instance.user.last_name = \
                self.cleaned_data.get('password1')
        self.instance.user.save()
        return super(UpdateProfileForm, self).save(*args, **kwargs)


class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = ("school", "creator")
