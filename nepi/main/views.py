from annoying.decorators import render_to
from django import forms
from django.contrib.auth import authenticate, login, logout
from nepi.main.models import Course, UserProfile, School, Country, LearningModule
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.contrib.auth.models import User
from django.template import Context, Template
from captcha.fields import CaptchaField



@render_to('main/index.html')
def index(request):
    return dict()

def about(request):
    """Returns about page."""
    return render_to_response('about.html')

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
                    #print("The password is valid, but the account has been disabled!")
            else:
                # the authentication system was unable to verify the username and password
                #print("The username and password were incorrect.")
                return HttpResponseRedirect("/")
    else:
        form = LoginForm()  # An unbound form

    return render(request, 'login.html', {
        'form': form,
    })

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

def help_page(request):
    """Returns help page."""
    return render_to_response('help.html')


def thank_you(request):
    """Returns about page."""
    return render_to_response('thanks.html')


def home(request):
    '''Return homepage appropriate for user type.'''
    user = request.user
    #print type(user)
    #print user.username
    #user = User.objects.get(username=user.username)
    user_profile = UserProfile.objects.get(user=user)
    if user_profile.profile_type == 'ST':
        t = Template('main/stindex.html')
        modules = LearningModule.objects.all()
        courses = user_profile.course.all()
        #Course.objects.filter(student=request.user.user_profile)
        c = Context({'modules' : modules, 'courses' : courses})
        return render(request, 'main/stindex.html', {'courses': courses, 'modules' : modules})
        #return HttpResponse(t.render(c))
        # course = models.ManyToManyField(Course)
        # return {'modules' : modules, 'courses' : courses}
        # return render_to_response('main/stindex.html')
    elif user_profile.profile_type == 'TE':
        return render_to_response('main/teindex.html')
    elif user_profile.profile_type == 'IC':
        return HttpResponseRedirect('/admin/')
    else:
        return HttpResponseRedirect('/')

def show_courses_and_modules(request):
    pass

def join_course(request):
    '''Have student select county and then school'''
    pass

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
                        #try:
                        #    get_school = School.objects.get(name=request.POST['school'])
                        #new_profile.country = request.POST['country']
                        new_profile.school = request.POST.get('school')
                        #WHY DOES DEFAULT VALUE HAVE TO BE SET HERE???
                        new_profile.profile_type = request.POST.get('is_teacher', 'ST')
                        new_profile.save()
                        return HttpResponseRedirect('/thank_you/')

            else:
                raise forms.ValidationError("You are missing a password.")

    else:
        form = CreateAccountForm()  # An unbound form

    return render(request, 'registration_form.html', {
        'form': form,
    })
############



def confirm_student(request):
    pass


def add_teacher(request):
    pass
    #teachers = teacher.objects.


def add_school(request):
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


def add_course(request):
    pass


def show_students(request):
    pass

def show_teachers(request):
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

    return render(request, 'main/contact.html', {
        'form': form,
    })


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, required=True)
    password = forms.CharField(widget=forms.PasswordInput, max_length=50, required=True)

class CreateAccountForm(forms.Form):
    '''This is a form class that will be used
    to allow guest users to create guest accounts.'''
    # all users should have immediate access to course material
    TEACHER = 'TE'
    STUDENT = 'ST'

    ACCOUNT_CHOICES = (
        (TEACHER, 'Teacher'),
        (STUDENT, 'Student'),
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
    country = forms.ChoiceField(widget=forms.Select(), choices=Country.COUNTRY_CHOICES, required=True)
    #forms.ModelChoiceField(queryset=Country.COUNTRY_CHOICES, required=False)
    #ChoiceField(widget=forms.Select(), choices=Country.COUNTRY_CHOICES, required=True)
    school = forms.ModelChoiceField(queryset=School.objects.all(), empty_label=None, required=False)#widget=forms.Select(), choices=School.objects.all(), required=False)
    is_teacher = forms.MultipleChoiceField(choices=ACCOUNT_CHOICES, initial='STUDENT') # WHY DOES INITIAL NOT WORK???
    #captcha = CaptchaField()


class AddTeacher(forms.Form):
    pass


class AddSchoolForm(forms.Form):
    name = forms.CharField(max_length=50, required=True, label="School Name")
    country = forms.ChoiceField(widget=forms.Select(), choices=Country.COUNTRY_CHOICES, required=True)


class AddCourse(forms.Form):
    semester = forms.CharField(max_length=50, required=True, label="Course Name")
    start_date = forms.DateField()#max_length=50, required=True, label="School Name")
    end_date = forms.DateField()#max_length=50, required=True, label="School Name")

class ContactForm(forms.Form):
    '''This is a form class that will be returned
    later in the contact form view.'''
    subject = forms.CharField(max_length=100, required=True)
    message = forms.CharField(max_length=500, required=True,
                              widget=forms.Textarea)
    sender = forms.EmailField(required=True)