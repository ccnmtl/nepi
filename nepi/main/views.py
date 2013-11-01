from annoying.decorators import render_to
from django import forms
from nepi.main.models import Student, ICAPStaff, Teacher, Course, UserProfile
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.contrib.auth.models import User
from registration.forms import RegistrationForm


@render_to('main/index.html')
def index(request):
    return dict()


def home(request):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    if user_profile.profile_type == 'ST':
        return render_to_response('main/stindex.html')
    elif user_profile.profile_type == 'TE':
        return render_to_response('main/teindex.html')
    elif user_profile.profile_type == 'IC':
        return HttpResponseRedirect('/admin/')
    else:
        return HttpResponseRedirect('/')


class CreateAccountForm(RegistrationForm):
    '''This is a form class that will be used
    to allow guest users to create guest accounts.'''
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


def register(request):
    '''This is based off of django-request - creates a new user account.'''
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        try:
            User.objects.get(username=request.POST['username'])
            raise forms.ValidationError("this username already exists")
        except User.DoesNotExist:
            if 'password1' in request.POST and 'password2' in request.POST:
                print "comparing passwords"
                if request.POST['password1'] != request.POST['password2']:
                    raise forms.ValidationError(
                        "passwords dont match each other")

                if request.POST['password1'] == request.POST['password2']:
                    new_user = User.objects.create_user(
                        username=request.POST['username'],
                        email=request.POST['email'],
                        password=request.POST['password1'])
                    new_user.first_name = request.POST['first_name']
                    new_user.last_name = request.POST['last_name']
                    new_user.save()
                    return HttpResponseRedirect('/thanks/')

            else:
                raise forms.ValidationError("You are missing a password.")

    else:
        form = CreateAccountForm()  # An unbound form

    return render(request, 'create_account.html', {
        'form': form,
    })


def confirm_student(request):
    pass


def add_teacher(request):
    pass


def add_school(request):
    pass


def add_course(request):
    pass


def contact(request):
    '''Contact someone regarding the project - WHO???'''
    if request.method == 'POST':  # If the form has been submitted...
        form = ContactForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            recipients = ['cdunlop@columbia.edu']
            from django.core.mail import send_mail
            send_mail(subject, message, sender, recipients)
            return render_to_response('thanks.html')
    else:
        form = ContactForm()  # An unbound form

    return render(request, 'contact.html', {
        'form': form,
    })


def about(request):
    """Returns about page."""
    return render_to_response('about.html')


def help_page(request):
    """Returns help page."""
    return render_to_response('help.html')
