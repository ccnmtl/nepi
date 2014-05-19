'''Views for NEPI, should probably break up
into smaller pieces.'''
from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from pagetree.generic.views import PageView, EditView, InstructorView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from nepi.main.forms import CreateAccountForm, ContactForm
from nepi.main.models import Course, UserProfile
from nepi.main.models import School, PendingTeachers
from django.views.generic.edit import FormView
from django.views.generic.edit import CreateView, UpdateView
from django.core.mail import send_mail
import json
from django.views.generic.list import ListView


class AjaxableResponseMixin(object):
    """
    Taken from Django Website
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return self.render_to_json_response(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return self.render_to_json_response(data)
        else:
            return response


class LoggedInMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(*args, **kwargs)


class LoggedInMixinStaff(object):
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixinStaff, self).dispatch(*args, **kwargs)


class LoggedInMixinSuperuser(object):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixinSuperuser, self).dispatch(*args, **kwargs)


class ViewPage(LoggedInMixin, PageView):
    template_name = "main/page.html"
    hierarchy_name = "main"
    hierarchy_base = "/pages/main/"
    gated = False


class EditPage(LoggedInMixinSuperuser, EditView):
    template_name = "main/edit_page.html"
    hierarchy_name = "main"
    hierarchy_base = "/pages/main/"


# this is from default pagetree
class InstructorPage(LoggedInMixinStaff, InstructorView):
    hierarchy_name = "main"
    hierarchy_base = "/pages/main/"


class ContactView(FormView):
    '''changed contact view function to
    generic class based view'''
    template_name = 'main/contact.html'
    form_class = ContactForm
    success_url = '/thanks/'

    def form_valid(self, form):
        '''should this be in the form instead?'''
        form_data = form.cleaned_data
        sender = form_data['sender'],
        subject = form_data['subject'],
        message = form_data['message'],
        recipients = ['cdunlop@columbia.edu']
        send_mail(subject, message, sender, recipients)
        return super(ContactView, self).form_valid(form)


def thanks_course(request, course_id):
    """Returns thanks for joining course page."""
    return render(request, 'student/thanks_course.html')


# when to use class based views vs generic class based views?
# can you just have classes inherit generic based views
# do mixin for being logged in?


@login_required
def home(request):
    '''Return homepage appropriate for user type.'''
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except User.DoesNotExist:
        profile = None
        return HttpResponseRedirect(reverse('register'))
    
    if user_profile.profile_type == 'ST':
        courses = user_profile.course.all()
        return render(request, 'student/stindex.html',
                      {'courses': courses})
    elif user_profile.profile_type == 'TE':
        pass
    elif user_profile.profile_type == 'IC':
        pending_teachers = PendingTeachers.objects.filter(
            user_profile__profile_type='TE')
        schools = School.objects.all()
        return render(request, 'icap/icindex.html',
                      {'schools': schools,
                          'pending_teachers': pending_teachers})
    else:
        return HttpResponseRedirect('/')


    # should there be methods for registering
    # teacher and checking country?
    # should form validation be done in the Form Class
    # or in the View
    # online see example with
    # form = CreateAccountForm(data=request.POST)
    # under class def does this mean if method post?
# confused a bit about whether validation
# and assigning variables is automatic...


class RegistrationView(FormView):
    '''changing registration view to form'''
    template_name = 'registration_form.html'
    form_class = CreateAccountForm
    success_url = '/thank_you_reg/'

    def form_valid(self, form):
        form_data = form.cleaned_data
        try:
            User.objects.get(username=form_data['username'])
            raise forms.ValidationError("this username already exists")
        except User.DoesNotExist:
            new_user = User.objects.create_user(
                username=form_data['username'],
                email=form_data['email'],
                password=form_data['password1'])
            new_user.first_name = form_data['first_name']
            new_user.last_name = form_data['last_name']
            new_user.save()
            new_profile = UserProfile(user=new_user)
            new_profile.profile_type = 'ST'
            new_profile.country = form_data['country']
            new_profile.save()
            if form_data['email']:
                subject = "NEPI Registration"
                message = "Congratulations! " + \
                          "You've successfully registered to use NEPI.\n\n" + \
                          "Your user information is " + \
                          form_data['username'] + \
                          ".\n\n" + \
                          "You may now log in to your account."
                sender = "nepi@nepi.ccnmtl.columbia.edu"
                recipients = [form_data['email']]
                send_mail(subject, message, sender, recipients)
            subject = "[Student] User Account Created"
            sender = "nepi@nepi.ccnmtl.columbia.edu"
            recipients = ["nepi@nepi.ccnmtl.columbia.edu"]
            message = form_data['username'] + \
                " has successfully created a NEPI account.\n\n"
            if form_data['profile_type']:
                subject = "[Teacher] Account Requested"
                message = form_data['first_name'] + \
                    " " + form_data['last_name'] + \
                    "has requested teacher status in "
                    # need to add country and schools here
                pending = PendingTeachers(user_profile=new_profile)
                pending.save()
                send_mail(subject, message, sender, recipients)
        return super(RegistrationView, self).form_valid(form)  # human = True

############
"""NEPI Peoples Views"""


class CreateSchoolView(CreateView):
    '''generic class based view for
    adding a school'''
    model = School
    template_name = 'icap/add_school.html'
    success_url = '/thank_you/'


class UpdateSchoolView(UpdateView):
    '''generic class based view for
    editing a school'''
    model = School
    template_name = 'icap/add_school.html'
    success_url = '/thank_you/'


"""Teacher Views"""


class CreateCourseView(CreateView):
    '''generic class based view for
    creating a course'''
    model = Course
    template_name = 'teacher/create_course.html'
    success_url = '/thank_you/'


class UpdateCourseView(UpdateView):
    '''generic class based view for
    editing a course'''
    model = Course
    template_name = 'teacher/create_course.html'
    success_url = '/thank_you/'


def course_students(request, crs_id):
    '''see all students in a particular course'''
    users = User.objects.all()
    course_students = []
    for u in users:
        try:
            profile = UserProfile.objects.get(user=u)
            if profile.profile_type == 'ST':
                courses = profile.course_set.all()
                for c in courses:
                    if c.crs_id == crs_id:
                        course_students.add(profile)
                        # [u][profile][c])
        except UserProfile.DoesNotExist:
            pass

    return render(request,
                  'teacher/show_students.html',
                  {'course_students': course_students})


def remove_student(request, stud_id, cors_id):
    """Allow teacher to remove student."""
    pass



class GrabCountryClasses(AjaxableResponseMixin, ListView):
    '''Not sure if it is better to grab a DetailView of Country courses or
    to do list view of Course for the Country'''



# def student_test_score(u_id, q_id):
#     '''see student score on exam'''
#     quizzes = Quiz.objects.all()
#     user_s = User.objects.get(pk=u_id)
#     profile = UserProfile.objects.get(user=user_s)
#
#     course_students = []
#     for u in users:
#         try:
#             profile = UserProfile.objects.get(user=u)
#             if profile.profile_type == 'ST':
#                 courses = profile.course_set.all()
#                 for c in courses:
#                     if c.crs_id == crs_id:
#                         course_students.add(profile)
#                         # [u][profile][c])
#         except UserProfile.DoesNotExist:
#             pass
#     course_students =
#     return render(request,
#                   'teacher/show_students.html',
#                   {'course_students': course_students})

def student_average(s_id):
    pass


"""Student Views"""


def join_course(request):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    country = user_profile.country
    schools = School.objects.filter(country=country)
    return render(request,
                  'student/join_course.html',
                  {'schools': schools,
                   'country': country
                   }
                  )


def view_courses(request, schl_id):
    school = School.objects.get(pk=schl_id)
    courses = Course.objects.filter(school=school)
    return render(request,
                  'student/view_courses.html',
                  {'courses': courses, 'school': school})
