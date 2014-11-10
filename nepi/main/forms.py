import re

from captcha.fields import CaptchaField
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.forms.fields import ChoiceField
from django.template import loader
from django.template.context import Context

from nepi.main.models import UserProfile, Country, School, PendingTeachers


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


class ChoiceFieldNoValidation(ChoiceField):
    def validate(self, value):
        return True


class UserProfileForm(forms.Form):
    first_name = forms.CharField(
        max_length=50, required=True)
    last_name = forms.CharField(
        max_length=50, required=True)
    username = forms.CharField(
        max_length=25, required=True)
    email = forms.EmailField(required=False)
    country = forms.ChoiceField(required=True)

    # School is not validated as it is variably required
    # Yes for teachers, No for students
    school = ChoiceFieldNoValidation(required=False)

    nepi_affiliated = forms.BooleanField(required=False)
    password1 = forms.CharField(
        max_length=25, widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(
        max_length=25, widget=forms.PasswordInput, required=True)
    profile_type = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields["country"].choices = Country.choices()

    def clean(self):
        cleaned_data = super(UserProfileForm, self).clean()
        is_teacher = cleaned_data.get("profile_type")
        email = cleaned_data.get("email")
        school = cleaned_data.get("school", None)
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        country = cleaned_data.get("country")

        if is_teacher:
            if email is None or email == "":
                self._errors["email"] = self.error_class(
                    ["If you are registering as an instructor " +
                     "you must enter a valid email address."])
            if (school == '-----' or
                    School.objects.filter(id=school).count() < 1):
                self._errors["school"] = self.error_class(
                    ["If you are registering as an instructor " +
                     "you must select a school."])

        if password1 != password2:
            self._errors["password1"] = self.error_class(
                ["Passwords must match each other."])
            self._errors["password2"] = self.error_class(
                ["Passwords must match each other."])

        if Country.objects.filter(name=country).count() < 1:
            self._errors['country'] = self.error_class([
                "This field is required."])

        return cleaned_data

    def send_success_email(self, user):
        template = loader.get_template(
            'registration/registration_success_email.txt')

        subject = "ICAP Nursing E-Learning Registration"

        ctx = Context({'user': user})
        message = template.render(ctx)

        sender = settings.NEPI_MAILING_LIST
        recipients = [user.email]
        send_mail(subject, message, sender, recipients)

    def send_teacher_notifiction(self, user, school):
        template = loader.get_template(
            'dashboard/faculty_request_email.txt')

        subject = "A request for faculty level access has " \
            "been submitted to the ICAP Nursing E-Learning system"

        ctx = Context({'user': user, 'school': school})
        message = template.render(ctx)

        sender = settings.NEPI_MAILING_LIST
        recipients = [settings.ICAP_MAILING_LIST]
        send_mail(subject, message, sender, recipients)

    def create_pending_teacher(self, user, school_id):
        school = School.objects.get(id=school_id)
        pending, created = PendingTeachers.objects.get_or_create(
            user_profile=user.profile, school=school)

        if created:
            self.send_teacher_notifiction(user, school)


class CreateAccountForm(UserProfileForm):
    captcha = CaptchaField()

    def clean(self):
        cleaned_data = super(CreateAccountForm, self).clean()

        username = cleaned_data.get("username")

        if (username is not None and len(username) > 0 and
                not re.search(r'^[\w.@+-]+$', username)):
            self._errors["username"] = self.error_class(
                ["Usernames can contain alphanumeric characters only "
                 "(letters, digits and underscores)."])
        elif User.objects.filter(username=username).count() > 0:
            self._errors["username"] = self.error_class(
                ["This username is taken. Please select a different one."])

        return cleaned_data

    def save(self, commit=True):
        form_data = self.cleaned_data

        new_user = User.objects.create_user(
            username=form_data['username'],
            email=form_data['email'],
            password=form_data['password1'])
        new_user.first_name = form_data['first_name']
        new_user.last_name = form_data['last_name']
        new_user.save()

        new_profile = UserProfile(user=new_user)
        new_profile.profile_type = 'ST'

        if 'nepi_affiliated' in form_data:
            new_profile.icap_affil = form_data['nepi_affiliated']

        country = Country.objects.get(name=form_data['country'])
        new_profile.country = country

        new_profile.save()

        # send the user a success email
        if new_user.email:
            self.send_success_email(new_user)

        if 'profile_type' in form_data and form_data['profile_type']:
            self.create_pending_teacher(new_profile.user, form_data['school'])


class UpdateProfileForm(UserProfileForm):
    def __init__(self, *args, **kwargs):
        self.base_fields['password1'].required = False
        self.base_fields['password2'].required = False

        user = kwargs.pop('instance', None)
        if user:
            kwargs['initial'] = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'email': user.email,
                'country': user.profile.country.name,
                'nepi_affiliated': user.profile.icap_affil
            }
            if user.profile.school:
                kwargs['initial']['school'] = user.profile.school.id
        super(UpdateProfileForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        form_data = self.cleaned_data

        user = User.objects.get(username=form_data.get('username'))
        profile = user.profile

        user.first_name = form_data.get('first_name')
        user.last_name = form_data.get('last_name')
        user.email = form_data.get('email')

        if (form_data.get('password1') and form_data.get('password2')):
            user.set_password(form_data.get('password1'))

        user.save()

        profile.icap_affil = form_data.get('nepi_affiliated')

        if user.profile.is_student() and not user.profile.is_pending_teacher():
            profile.country = Country.objects.get(
                name=form_data.get('country'))
        profile.save()

        profile_type = form_data.get('profile_type', False)
        if not profile.is_pending_teacher() and profile_type:
            self.create_pending_teacher(user, form_data.get('school'))
