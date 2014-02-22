from annoying.decorators import render_to
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, render_to_response
from nepi.main.forms import CreateAccountForm, ContactForm, \
    CaptchaTestForm, LoginForm
from nepi.main.models import Country, Course, UserProfile
from nepi.main.models import School, PendingTeachers
from pagetree.helpers import get_section_from_path, get_module, needs_submit
import json
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse
from django.views.generic.base import View
from django.views.generic.edit import CreateView, UpdateView
#from django.views.generic.edit import ListView


@user_passes_test(lambda u: u.is_superuser)
@render_to('main/edit_page.html')
def edit_page(request, hierarchy, path):
    section = get_section_from_path(path, hierarchy)
    first_leaf = section.hierarchy.get_first_leaf(section)

    return dict(section=section,
                module=get_module(section),
                root=section.hierarchy.get_root(),
                leftnav=_get_left_parent(first_leaf),
                prev=first_leaf.get_previous(),
                next=first_leaf.get_next())


@login_required
@render_to('main/page.html')
def page(request, hierarchy, path):
    section = get_section_from_path(path, hierarchy)
    return _response(request, section, path)


def _get_left_parent(first_leaf):
    leftnav = first_leaf
    if first_leaf.depth == 4:
        leftnav = first_leaf.get_parent()
    elif first_leaf.depth == 5:
        leftnav = first_leaf.get_parent().get_parent()
    return leftnav


def _response(request, section, path):
    h = section.hierarchy
    if request.method == "POST":
        # user has submitted a form. deal with it
        proceed = True
        for p in section.pageblock_set.all():
            if hasattr(p.block(), 'needs_submit'):
                if p.block().needs_submit():
                    prefix = "pageblock-%d-" % p.id
                    data = dict()
                    for k in request.POST.keys():
                        if k.startswith(prefix):
                            data[k[len(prefix):]] = request.POST[k]
                    p.block().submit(request.user, data)
                    if hasattr(p.block(), 'redirect_to_self_on_submit'):
                        proceed = not p.block().redirect_to_self_on_submit()

        if request.is_ajax():
            j = json.dumps({'submitted': 'True'})
            return HttpResponse(j, 'application/json')
        elif proceed:
            return HttpResponseRedirect(section.get_next().get_absolute_url())
        else:
            # giving them feedback before they proceed
            return HttpResponseRedirect(section.get_absolute_url())
    else:
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            profile = UserProfile(user=request.user,
                                  profile_type='ST')
            profile.save()

        # the previous node is the last leaf, if one exists.
        prev = section.get_previous()
        next_page = section.get_next()

        # Is this section unlocked now?
        can_access = section.gate_check(request.user)
        if can_access:
            profile.set_has_visited([section])

        return dict(section=section,
                    needs_submit=needs_submit(section),
                    accessible=can_access,
                    root=h.get_root(),
                    previous=prev,
                    next=next_page,
                    depth=section.depth,
                    request=request,
                    next_unlocked=(next_page is not None and
                                   next_page.gate_check(request.user)))


def test_view(request):
    form = CaptchaTestForm()
    if request.POST:
        form = CaptchaTestForm(request.POST)
        # Validate the form: the captcha field will automatically
        # check the input
        if form.is_valid():
            human = True
    else:
        form = CaptchaTestForm()

    return render_to_response("main/test_view.html", locals())


def captchatest(request):
    if request.POST:
        form = CaptchaTestForm(request.POST)
        # Validate the form: the captcha field will automatically
        # check the input
        if form.is_valid():
            human = True
    else:
        form = CaptchaTestForm()

    return render_to_response("main/captchatest.html", locals())


"""General Views"""


@login_required
@render_to('main/index.html')
def index(request):
    return dict()


def logout_view(request):
    """When user logs out redirect to home page."""
    logout(request)
    return HttpResponseRedirect('/')


class ContactView(FormView):
    template_name = 'main/contact.html'
    form_class = ContactForm
    success_url = '/thanks/'

    form_data = form.cleaned_data

    def form_valid(self, form):
        if self.request.method == 'POST':
            sender = self.request.POST['sender'],
            subject = self.request.POST['subject'],
            message = self.request.POST['message'],
            from django.core.mail import send_mail
            recipients = ['cdunlop@columbia.edu']
            send_mail(subject, message, sender, recipients)
        #else:
        #    data = None
        return super(ContactView, self).form_valid(form)


def thanks_course(request, course_id):
    """Returns thanks for joining course page."""
    return render(request, 'student/thanks_course.html')


"""More General Views"""


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


# when to use class based views vs generic class based views?
# can you just have classes inherit generic based views
# do mixin for being logged in?
def home(request):
    '''Return homepage appropriate for user type.'''
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.profile_type == 'ST':
            courses = user_profile.course.all()
            return render(request, 'student/stindex.html',
                          {'courses': courses})

        elif user_profile.profile_type == 'TE':
            pass
        elif user_profile.profile_type == 'IC':
            pending_teachers = PendingRegister.objects.filter(
                profile_type='TE')
            schools = School.objects.all()
            return render(request, 'icap/icindex.html',
                          {'schools': schools,
                              'pending_teachers': pending_teachers})
        else:
            return HttpResponseRedirect('/')
    except User.DoesNotExist:
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
        # this prints so it is definately valid
        # print self.request.method
        form_data = form.cleaned_data
        if 'password1' not in form_data \
                or 'password2' not in form_data:
            raise forms.ValidationError("You are missing a password.")
        if form_data['password1'] \
                != form_data['password2']:
            raise forms.ValidationError(
                        "passwords dont match each other")
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
            new_profile.save()
            if form_data['profile_type'] == 'TE':
                pending = PendingTeachers(user_profile=new_profile)
                pending.save()
        return super(RegistrationView, self).form_valid(form)


############
"""NEPI Peoples Views"""


class CreateSchoolView(CreateView):
    model = School
    template_name = 'icap/add_school.html'
    success_url = '/thank_you/'


class UpdateSchoolView(UpdateView):
    model = School
    template_name = 'icap/add_school.html'
    success_url = '/thank_you/'


"""Teacher Views"""
# django site says to do this way but throws errors...


class CreateCourseView(CreateView):
    model = Course
    template_name = 'teacher/create_course.html'
    success_url = '/thank_you/'


class UpdateCourseView(UpdateView):
    model = Course
    template_name = 'teacher/create_course.html'
    success_url = '/thank_you/'


def course_students(request, crs_id):
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


def course_results(request):
    pass


def course_created(request):
    pass


"""Student Views"""


#def find_course(request):
#    pass


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
