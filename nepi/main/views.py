'''Views for NEPI, should probably break up
into smaller pieces.'''
from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from pagetree.generic.views import PageView, EditView, InstructorView
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from nepi.main.forms import CreateAccountForm, ContactForm, UpdateProfileForm
from nepi.main.models import Course, UserProfile, Country
from nepi.main.models import School, PendingTeachers
from django.views.generic.edit import FormView
from django.views.generic.edit import CreateView, UpdateView
from django.core.mail import send_mail
import json
from django.views.generic import View
from django.core.urlresolvers import reverse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from pagetree.models import Hierarchy
from nepi.main.forms import CreateCourseForm
from django.views.generic.edit import DeleteView
from django.core.urlresolvers import reverse_lazy


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

# should make a class to say thank you for... and give appropriate statement.
class ThankYou(View):
    def get(self, request):
        '''not entirely sure how thise will be called yet...
        need to determine how we will indicate what the situation is...'''
        if request.is_ajax():
            pass
#             if get
#             pk=self.request.POST.__getitem__('country'))

    def post(self, request):
        '''again not entirely sure how this is going to be called'''
        pass



def thanks_course(request, course_id):
    """Returns thanks for joining course page."""
    return render(request, 'student/thanks_course.html')


class Home(View):
    '''redoing so that it simply redirects people where they need to be'''

    def get(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user.pk)
        except User.DoesNotExist:
            return HttpResponseRedirect(reverse('register'))
        if user_profile.profile_type == 'ST':
            return HttpResponseRedirect(reverse('student-dashboard'))
            # return HttpResponseRedirect(reverse('student-dashboard',
            #    {'pk' : profile.pk}))
        elif user_profile.profile_type == 'TE':
            return HttpResponseRedirect(reverse('faculty-dashboard'))
        elif user_profile.profile_type == 'IC':
            return HttpResponseRedirect(reverse('icap-dashboard'))
        else:
            '''I assume it could be possible another
            app has a profile_type variable?'''
            return HttpResponseRedirect(reverse('register'))


class ICAPDashboard(LoggedInMixin, ListView):
    model = Course
    template_name = 'dashboard/icap_dashboard.html'
    success_url = '/'

    def get_students_in_progress(self):
        find_students = UserProfile.objects.filter(profile_type="ST")
        in_progress = 0
        for each in find_students:
            if each.percent_complete() != 0 and each.percent_complete() != 100:
                in_progress = in_progress + 1
        return in_progress

    def get_students_incomplete(self):
        find_students = UserProfile.objects.filter(profile_type="ST")
        incomplete = 0
        for each in find_students:
            if each.percent_complete() != 0 and each.percent_complete() != 100:
                incomplete = incomplete + 1
            return incomplete

    def get_students_done(self):
        find_students = UserProfile.objects.filter(profile_type="ST")
        done = 0
        for each in find_students:
            if each.percent_complete() == 100:
                done = done + 1
        return done

    def get_context_data(self, **kwargs):
        context = super(ICAPDashboard, self).get_context_data(**kwargs)
        context['user_profile'] = UserProfile.objects.get(
            user=self.request.user.pk)
        context['pending_teachers'] = PendingTeachers.objects.filter(
            user_profile__profile_type='TE')
        context['students'] = UserProfile.objects.filter(
            profile_type="ST").count()
        context['in_progress'] = self.get_students_in_progress()
        context['incomplete'] = self.get_students_done()
        context['done'] = self.get_students_incomplete()
        context['created_courses'] = Course.objects.filter(
            creator=User.objects.get(pk=self.request.user.pk))
        context['joined_courses'] = UserProfile.objects.get(
            user=self.request.user.pk).course.all()
#             user=self.request.user.pk)
        # context['create_course'] = CreateCourse.as_view()
        return context


class FacultyDashboard(LoggedInMixin, ListView):
    model = Course
    template_name = 'dashboard/faculty_dashboard.html'
    success_url = '/'

    def get_students_in_progress(self):
        find_students = UserProfile.objects.filter(profile_type="ST")
        in_progress = 0
        for each in find_students:
            if each.percent_complete() != 0 and each.percent_complete() != 100:
                in_progress = in_progress + 1
        return in_progress

    def get_students_incomplete(self):
        find_students = UserProfile.objects.filter(profile_type="ST")
        incomplete = 0
        for each in find_students:
            if each.percent_complete() != 0 and each.percent_complete() != 100:
                incomplete = incomplete + 1
            return incomplete

    def get_students_done(self):
        find_students = UserProfile.objects.filter(profile_type="ST")
        done = 0
        for each in find_students:
            if each.percent_complete() == 100:
                done = done + 1
        return done

    def get_context_data(self, **kwargs):
        context = super(FacultyDashboard, self).get_context_data(**kwargs)
        # teacher = UserProfile.objects.get(user=request.user.pk)
        return context
#         students = UserProfile.objects.filter(profile_type="ST").count()
#         find_students = UserProfile.objects.filter(profile_type="ST")
#         in_progress = 0
#         incomplete = 0
#         done = 0
#         for each in find_students:
#             if each.percent_complete() != 0 and
# each.percent_complete() != 100:
#                 in_progress = in_progress + 1
#                 incomplete = incomplete + 1
#             if each.percent_complete() == 100:
#                 done = done + 1
#         return render(request, 'icap_dashboard.html',
#                       {'pending_teachers': pending_teachers,
#                        'user_profile': user_profile,
#                        'students': students, 'incomplete': incomplete,
# #                        'in_progress': in_progress, 'done': done})
#     def get_context_data(self, **kwargs):
#         context = super(ICAPDashboard, self).get_context_data(**kwargs)
#         context['user_profile'] = UserProfile.objects.get(
#             user=self.request.user.pk)
#         context['pending_teachers'] = PendingTeachers.objects.filter(
#             user_profile__profile_type='TE')
#         context['students'] = UserProfile.objects.filter(
#             profile_type="ST").count()
#         context['in_progress'] = self.get_students_in_progress()
#         context['incomplete'] = self.get_students_done()
#         context['done'] = self.get_students_incomplete()
#         context['created_courses'] = Course.objects.filter(
#             creator=User.objects.get(pk=self.request.user.pk))
#         context['joined_courses'] = UserProfile.objects.get(
#             user=self.request.user.pk).course.all()
# #             user=self.request.user.pk)
#         # context['create_course'] = CreateCourse.as_view()
#        return context

class StudentDashboard(LoggedInMixin, DetailView):
    '''For the first tab of the dashboard we are showing
    courses that the user belongs to, and if they do not belong to any
    we are giving the the option to affiliate with one'''
    model = UserProfile
    template_name = 'dashboard/student_dashboard.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(StudentDashboard, self).get_context_data(**kwargs)
        profile = UserProfile.objects.get(user=self.request.user.pk)
        context['user_profile'] = UserProfile.objects.get(
            user=self.request.user.pk)
        context['modules'] = Hierarchy.objects.all()
        context['user_modules'] = Hierarchy.objects.filter(userprofile=profile)
        context['student_courses'] = Course.objects.filter(userprofile=profile)
        # context['student_courses'] = profiles.course.all()


class GetReport(LoggedInMixin, View):
    template_name = 'dashboard.html'

    def post(self, request):
        if self.request.is_ajax():
            user_id = request.user.pk
            user_profile = UserProfile.objects.get(user=user_id)
            user_profile.country = Country.objects.get(
                pk=self.request.POST.__getitem__('country'))
            user_profile.school = School.objects.get(
                pk=self.request.POST.__getitem__('school'))
            user_profile.course = Course.objects.filter(
                pk=self.request.POST.__getitem__('course'))
            user_profile.save()
            return self.render_to_json_response(user_profile)
        else:
            return self.request


class JoinCourse(LoggedInMixin, View):
    template_name = 'student_dashboard.html'
    #success_url = '/thank_you/'

    def post(self, request):
        if self.request.is_ajax():
            user_id = request.user.pk
            user_profile = UserProfile.objects.get(user=user_id)
            user_profile.country = Country.objects.get(
                pk=self.request.POST.__getitem__('country'))
            user_profile.school = School.objects.get(
                pk=self.request.POST.__getitem__('school'))
            user_profile.course = Course.objects.filter(
                pk=self.request.POST.__getitem__('course'))
            user_profile.save()
            return self.render_to_json_response(user_profile)
        else:
            return self.request


class GetCountries(LoggedInMixin, ListView):
    model = Country
    template_name = 'dashboard/country_list.html'
    success_url = '/'


class GetCountrySchools(LoggedInMixin, ListView):
    model = School
    template_name = 'dashboard/school_list.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        if self.request.is_ajax():
            country_key = self.request.GET.__getitem__('name')
            country = Country.objects.get(pk=country_key)
            s = School.objects.filter(country=country)
            return {'school_list': s}


class GetSchoolCourses(LoggedInMixin, ListView):
    model = Course
    template_name = 'dashboard/course_list.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        if self.request.is_ajax():
            school_key = self.request.GET.__getitem__('name')
            school = School.objects.get(pk=school_key)
            course_list = Course.objects.filter(school=school)
            return {'course_list': course_list}


class RegistrationView(FormView):
    '''changing registration view to form'''
    template_name = 'registration_form.html'
    form_class = CreateAccountForm
    success_url = '/'

    def register_user(self):
        pass

    def register_profile(self):
        pass

    def send_student_email(self):
        pass

    def send_teacher_notifiction(self):
        pass

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
            try:
                new_profile.country = Country.objects.get(
                    name=form_data['country'])
                new_profile.save()
            except Country.DoesNotExist:
                new_country = Country.objects.create(name=form_data['country'])
                new_country.save()
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
            recipients = ["nepi@nepi.ccnmtl.columbia.edu"]
            if form_data['profile_type']:
                print form_data['profile_type']
                subject = "[Teacher] Account Requested"
                message = form_data['first_name'] + \
                    " " + form_data['last_name'] + \
                    "has requested teacher status in "
                    # need to add country and schools here
                pending = PendingTeachers.objects.create(
                    user_profile=new_profile)
                pending.save()
                send_mail(subject, message, sender, recipients)
        return super(RegistrationView, self).form_valid(form)


class CreateSchoolView(CreateView):
    '''generic class based view for
    adding a school'''
    model = School
    template_name = 'icap/add_school.html'
    success_url = '/'


class UpdateSchoolView(UpdateView):
    '''generic class based view for
    editing a school'''
    model = School
    template_name = 'icap/add_school.html'
    success_url = '/'


# LoggedInMixin,
class CreateCourseView(CreateView):
    '''generic class based view for
    creating a course'''
    model = Course
    form_class = CreateCourseForm
    template_name = 'dashboard/create_course.html'
    success_url = '/'

    def form_valid(self, request):
        f = CreateCourseForm(self.request.POST)
        new_course = f.save(commit=False)
        creator = User.objects.get(pk=self.request.user.pk)
        profile = UserProfile.objects.get(user=creator)
        school = School.objects.get(pk=profile.school.pk)
        new_course.creator = creator
        new_course.school = school
        new_course.save()
        # why do I need to return an HTTPResponse explicitly?
        # Should happen automatically no?
        return HttpResponseRedirect('/')


class AddCourse(CreateView):
    '''generic class based view for
    creating a course'''
    model = Course
    form_class = CreateCourseForm
    template_name = 'new_course.html'
    success_url = '/'

    def form_valid(self, request):
        f = CreateCourseForm(self.request.POST)
        new_course = f.save(commit=False)
        creator = User.objects.get(pk=self.request.user.pk)
        profile = UserProfile.objects.get(user=creator)
        school = School.objects.get(pk=profile.school.pk)
        new_course.creator = creator
        new_course.school = school
        new_course.save()
        # why do I need to return an HTTPResponse explicitly?
        # Should happen automatically no?
        return HttpResponseRedirect('/')


class UpdateCourseView(UpdateView):
    '''generic class based view for
    editing a course'''
    model = Course
    template_name = 'dashboard/create_course.html'
    success_url = '/'
    form_class = CreateCourseForm


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
        except UserProfile.DoesNotExist:
            pass

    return render(request,
                  'teacher/show_students.html',
                  {'course_students': course_students})


def remove_student(request, stud_id, cors_id):
    """Allow teacher to remove student."""
    pass


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
        recipients = ['nepi@nepi.ccnmtl.columbia.edu']#["u'cdunlop@columbia.edu'"]
        send_mail(subject, message, sender, 'nepi@nepi.ccnmtl.columbia.edu')
        form.send_email(recipients)
        return super(ContactView, self).form_valid(form)


class DeleteCourseView(DeleteView):
    model = Course
    success_url = reverse_lazy('home')

    def dispatch(self, *args, **kwargs):
        resp = super(DeleteCourseView, self).dispatch(*args, **kwargs)
        if self.request.is_ajax():
            response_data = {"result": "ok"}
            return HttpResponse(json.dumps(response_data),
                                content_type="application/json")
        else:
            # POST request (not ajax) will do a redirect to success_url
            return resp


class StudentClassStatView(DetailView):
    model = Course
    template_name = 'view_course_stats.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        if self.request.is_ajax():
            module = self.course.__module
            user = User.objects.get(pk=self.request.user.pk)
            profile = UserProfile.objects.get(user=user)
            return {'module': module, 'user': user, 'profile': profile}


class UpdateProfileView(UpdateView):
    model = UserProfile
    template_name = 'profile_tab.html'
    form_class = UpdateProfileForm
    success_url = '/'

    def form_valid(self, form):
        response = super(UpdateProfileView, self).form_valid(form)
        form_data = form.cleaned_data
        if form_data['faculty_access']:
            subject = "Facutly Access Requeted"
            message = "The user, " + form_data['first_name'] + \
                " " + form_data['last_name'] + " from " + \
                form_data['country'] + " has requested faculty " + \
                "faculty access at " + form_data['school'] + ".\n\n"
            sender = "nepi@nepi.ccnmtl.columbia.edu"
            recipients = "cdunlop@columbia.edu"
            send_mail(subject, message, sender, recipients)
        # not clear to me what validation is done for you
        form_data.save()
            
    def form_invalid(self, form):
        response = super(UpdateProfileView, self).form_invalid(form)
        if self.request.is_ajax():
            return self.render_to_json_response(form.errors, status=400)
        else:
            return response



class FacultyCountries(LoggedInMixin, ListView):
    model = Country
    template_name = 'faculty/country_list.html'
    success_url = '/'


class FacultyCountrySchools(LoggedInMixin, ListView):
    model = School
    template_name = 'faculty/school_list.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        if self.request.is_ajax():
            country_key = self.request.GET.__getitem__('name')
            country = Country.objects.get(pk=country_key)
            s = School.objects.filter(country=country)
            return {'school_list': s}
