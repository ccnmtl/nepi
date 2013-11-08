from annoying.decorators import render_to
from django import forms
from django.contrib.auth import authenticate, login, logout
from nepi.main.models import Course, UserProfile, School, Country, LearningModule, PendingRegister
from nepi.main.forms import LoginForm, CreateAccountForm, AddTeacher, AddSchoolForm, AddCourse, ContactForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.contrib.auth.models import User
from django.template import Context, Template
import json
#from captcha.fields import CaptchaField
from django.utils import simplejson
from django.views.generic.detail import BaseDetailView, \
    SingleObjectTemplateResponseMixin



@render_to('main/index.html')
def index(request):
    return dict()


def about(request):
    """Returns about page."""
    return render_to_response('about.html')


def logout_view(request):
    """When user logs out redirect to home page."""
    logout(request)
    return HttpResponseRedirect('/')


def help_page(request):
    """Returns help page."""
    return render_to_response('help.html')


def thank_you(request):
    """Returns thanks for registering page."""
    return render_to_response('main/thanks.html')


def thanks_course(request, course_id):
    """Returns thanks for joining course page."""
    return render(request, 'main/thanks_course.html', { 'form': form, })


def nepi_login(request):
    '''Allow user to login.'''
    if request.method == 'POST':  # If the form has been submitted...
        form = LoginForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect("/home/")
                else:
                    return HttpResponseRedirect("/")
            else:
                return HttpResponseRedirect("/")
    else:
        form = LoginForm()  # An unbound form

    return render(request, 'main/login.html', {
        'form': form,
    })


def home(request):
    '''Return homepage appropriate for user type.'''
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    if user_profile.profile_type == 'ST':
        modules = LearningModule.objects.all()
        courses = user_profile.course.all()
        return render(request, 'main/stindex.html', {'courses': courses, 'modules' : modules})
    elif user_profile.profile_type == 'TE':
        pending_students = PendingRegister.objects.filter(profile_type='ST')
        courses = user_profile.course.all()
        return render(request, 'main/teindex.html', {'courses': courses, 'pending_students' : pending_students})
    elif user_profile.profile_type == 'IC':
        return HttpResponseRedirect('main/icindex.html/')
    else:
        return HttpResponseRedirect('/')


def register(request):
    '''This is based off of django-request - creates a new user account.'''
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        if form.is_valid():
            human = True
            try:
                User.objects.get(username=request.POST['username'])
                raise forms.ValidationError("this username already exists")
                #TODO: should probably check provided email as well
            except User.DoesNotExist:
                if 'password1' in request.POST and 'password2' in request.POST:
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
                        new_profile = UserProfile(user=new_user)
                        try:
                            get_country = Country.objects.get(country=request.POST['country'])
                            new_profile.country = get_country
                            new_profile.save()
                        except Country.DoesNotExist:
                            get_country = Country(country=request.POST['country'])
                            get_country.save()
                            new_profile.country = get_country
                            new_profile.save()
                        new_profile.profile_type = 'ST'
                        is_teacher = request.POST.get('is_teacher', 'ST')
                        if is_teacher == 'TE':
                            new_profile.status_request = True
                            new_profile.save()
                            recipients = ['cdunlop@columbia.edu']
                            if request.POST['email']:
                                sender = request.POST['email']
                            else:
                                sender = "unknown@unknown.com"
                            subject = 'Teacher Status Requested'
                            message = str(new_user.first_name) + " " + str(new_user.last_name) + " has requested teacher status at " #+ get_school.name + "."
                            from django.core.mail import send_mail
                            send_mail(subject, message, sender, recipients)
                            return render_to_response('main/thanks_teacher.html')
                        new_profile.save()
                        return HttpResponseRedirect('/thank_you/')

            else:
                raise forms.ValidationError("You are missing a password.")

    else:
        form = CreateAccountForm()

    return render(request, 'registration_form.html', {
        'form': form,
    })


############


def conf_teacher(request):
    """This is intended to be for ICAP personel to confirm teachers in the program."""
    user_info = User.objects.getprofile(is_teacher=True)
    conf_teach = UserProfile.objects.filter(is_teacher=True)
    return render(request, 'main/show_teachers.html', {'conf_teach': conf_teach})

def create_course(request):
    pass

def add_school(request):
    """This is intended to be for ICAP personel to register Schools in the program."""
    if request.method == 'POST':
        form = AddSchoolForm(request.POST)
        try:
            get_country = Country.objects.get(country=request.POST['country'])
            try:
                School.objects.get(name=request.POST['name'], country=get_country)
                raise forms.ValidationError("This school already exists.")
            except School.DoesNotExist:
                new_school = School(
                    name=request.POST['name'],
                    country = get_country
                )
                new_school.save()
                return HttpResponseRedirect('/thank_you/')
        except Country.DoesNotExist:
            new_country = Country(country=request.POST['country'])
            new_country.save()
            new_school = School(
                name=request.POST['name'],
                country = new_country
            )
            new_school.save()
            return HttpResponseRedirect('/thank_you/')

    else:
        form = AddSchoolForm()  # An unbound form

    return render(request, 'add_school.html', {
        'form': form,
    })


def join_course(request):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    country = user_profile.country
    schools = School.objects.filter(country=country)
    return render(request, 'main/join_course.html', {'schools' : schools, 'country' : country})

def view_courses(request, schl_id):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    school = School.objects.get(pk=schl_id)
    courses = Course.objects.filter(school=school)
    return render(request, 'main/view_courses.html', {'courses' : courses, 'school' : school})

def add_course(request, crs_id):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    course = Course.objects.get(pk=crs_id)
    register = PendingRegister(user=user, userprofile=user_profile, course=course)
    register.save()
    return render(request, 'main/thanks_course.html', {'course' : course})


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

    return render(request, 'main/contact.html', {
        'form': form,
    })





# This is an experimental view involving an external registration table - this is to temporarily store requests from Teachers and Students
# to be associated with a course or school


def table_register(request):
    '''This is based off of django-request - creates a new user account.'''
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        if form.is_valid():
            try:
                User.objects.get(username=request.POST['username'])
                raise forms.ValidationError("this username already exists")
            except User.DoesNotExist:
                if 'password1' in request.POST and 'password2' in request.POST:
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
                        new_profile = UserProfile(user=new_user)
                        try:
                            get_country = Country.objects.get(country=request.POST['country'])
                            new_profile.country = get_country
                            new_profile.save()
                        except Country.DoesNotExist:
                            get_country = Country(country=request.POST['country'])
                            get_country.save()
                            new_profile.country = get_country
                            new_profile.save()
                        new_profile.profile_type = 'ST'
                        new_profile.save() # This should be the end of the user profile - everything else - whether
                        #they claim to be a student in a course or a teacher at a school should be stored until it is verified
                        is_teacher = request.POST.get('is_teacher', 'ST')
                        if is_teacher == 'TE':
                            # verified the following lines with print statements
                            register = PendingRegister(user=new_user, userprofile=new_profile, profile_type='TE')
                            register.save()
                            recipients = ['cdunlop@columbia.edu']
                            if request.POST['email']:
                                sender = request.POST['email']
                            else:
                                sender = "unknown@unknown.com"
                            subject = 'Teacher Status Requested'
                            message = str(new_user.first_name) + " " + str(new_user.last_name) + " has requested teacher status." #+ get_school.name + "."
                            from django.core.mail import send_mail
                            send_mail(subject, message, sender, recipients)
                            return render_to_response('main/thanks_teacher.html')
                        return HttpResponseRedirect('/thank_you/')

            else:
                raise forms.ValidationError("You are missing a password.")

    else:
        form = CreateAccountForm()

    return render(request, 'registration_form.html', {
        'form': form,
    })



def confirm(request):
    # Grab all pending teacher requests
    conf_teach = PendingRegister.objects.filter(profile_type='TE')
    return render(request, 'main/show_teachers.html', { 'conf_teach' : conf_teach })#, 'school_list' : school_list })



def confirm_teacher(request, prof_id, schl_id):
    userprofile = UserProfile.object.get(pk=prof_id)
    school = School.object.get(pk=schl_id)
    userprofile.profile_type = 'TE'
    userprofile.school = school
    userprofile.save()
    return HttpResponseRedirect('/confirm/')


def deny_teacher(request, prof_id, schl_id):
    pass


def confirm_student(request, st_id, class_id):
    userprofile = UserProfile.object.get(pk=prof_id)
    course = Course.object.get(pk=st_id)
    userprofile.course = course
    userprofile.school = course.school
    userprofile.save()
    return HttpResponseRedirect('/confirm/')

def deny_student(request, prof_id, schl_id):
    pass


def view_students(request):
    """"""
    pass

def view_schools(request):
    """"""
    pass

def view_region(request):
    """"""
    pass