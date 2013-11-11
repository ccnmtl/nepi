from django import forms
from nepi.main.models import Course, UserProfile, School, Country
from nepi.main.models import LearningModule


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, required=True)
    password = forms.CharField(widget=forms.PasswordInput, max_length=50, required=True)



class CreateAccountForm(forms.Form):
    '''This is a form class that will be used
    to allow guest users to create guest accounts.'''
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
    is_teacher = forms.MultipleChoiceField(choices=ACCOUNT_CHOICES, initial='STUDENT')


class ContactForm(forms.Form):
    '''This is a form class that will be returned
    later in the contact form view.'''
    subject = forms.CharField(max_length=100, required=True)
    message = forms.CharField(max_length=500, required=True,
                              widget=forms.Textarea)
    sender = forms.EmailField(required=True)


class AddTeacher(forms.Form):
    pass


class AddSchoolForm(forms.Form):
    name = forms.CharField(max_length=50, required=True, label="School Name")
    country = forms.ChoiceField(widget=forms.Select(), choices=Country.COUNTRY_CHOICES, required=True)


class CreateCourseForm(forms.Form):
    name = forms.CharField(max_length=50, required=True, label="Course Name")
    semester = forms.CharField(max_length=50, required=True, label="Semester")
    start_date = forms.DateField()
    end_date = forms.DateField()


    
#class JoinCourse(forms.Form):
#    '''Allow student to join course - return page to search for school by country.'''
