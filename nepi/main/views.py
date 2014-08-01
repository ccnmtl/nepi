'''Views for NEPI, should probably break up
into smaller pieces.'''
from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.template import loader
from django.template.context import Context
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView, FormView, CreateView, \
    UpdateView
from django.views.generic.list import ListView
from nepi.activities.views import JSONResponseMixin
from nepi.main.choices import COUNTRY_CHOICES
from nepi.main.forms import CreateAccountForm, ContactForm, \
    UpdateProfileForm, CreateGroupForm
from nepi.main.models import Group, UserProfile, Country, School, \
    PendingTeachers
from pagetree.generic.views import PageView, EditView, InstructorView
from pagetree.models import Hierarchy, UserPageVisit
import json


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

    def get_extra_context(self):
        menu = []
        visits = UserPageVisit.objects.filter(user=self.request.user,
                                              status='complete')
        visit_ids = visits.values_list('section__id', flat=True)

        previous_unlocked = True
        for section in self.root.get_descendants():
            unlocked = section.id in visit_ids
            item = {
                'id': section.id,
                'url': section.get_absolute_url(),
                'label': section.label,
                'depth': section.depth,
                'disabled': not (previous_unlocked or section.id in visit_ids)
            }
            menu.append(item)
            previous_unlocked = unlocked

        return {'menu': menu}


class EditPage(LoggedInMixinSuperuser, EditView):
    template_name = "main/edit_page.html"
    hierarchy_name = "main"
    hierarchy_base = "/pages/main/"


# this is from default pagetree
class InstructorPage(LoggedInMixinStaff, InstructorView):
    hierarchy_name = "main"
    hierarchy_base = "/pages/main/"


class ThanksGroupView(LoggedInMixin, TemplateView):
    template_name = 'student/thanks_group.html'


class Home(LoggedInMixin, View):
    '''redoing so that it simply redirects people where they need to be'''

    def get(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user.pk)
        except UserProfile.DoesNotExist:
            return HttpResponseRedirect(reverse('register'))
        if user_profile.profile_type == 'ST':
            return HttpResponseRedirect(reverse('student-dashboard',
                                        kwargs={'pk': user_profile.pk}))
            # return HttpResponseRedirect(reverse('student-dashboard',
            #    {'pk' : profile.pk})) # {% url 'news-year-archive' yearvar %}"
        elif user_profile.profile_type == 'TE':
            return HttpResponseRedirect(reverse('faculty-dashboard',
                                        kwargs={'pk': user_profile.pk}))
        elif user_profile.profile_type == 'IC':
            return HttpResponseRedirect(reverse('icap-dashboard',
                                        kwargs={'pk': user_profile.pk}))
        else:
            '''I assume it could be possible another
            app has a profile_type variable?'''
            return HttpResponseRedirect(reverse('register'))


class StudentDashboard(LoggedInMixin, DetailView):
    '''For the first tab of the dashboard we are showing
    groups that the user belongs to, and if they do not belong to any
    we are giving the the option to affiliate with one'''
    model = UserProfile
    template_name = 'dashboard/icap_dashboard.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(StudentDashboard, self).get_context_data(**kwargs)
        context['modules'] = Hierarchy.objects.all()
        return context


class FacultyDashboard(StudentDashboard):
    '''Dashboard that Faculty sees, have the added ability to see
    the students in their courses and their progress.'''
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
        context = super(FacultyDashboard, self).get_context_data(**kwargs)
        context['students'] = UserProfile.objects.filter(
            profile_type="ST").count()
        context['in_progress'] = self.get_students_in_progress()
        context['incomplete'] = self.get_students_done()
        context['done'] = self.get_students_incomplete()
        context['created_groups'] = Group.objects.filter(
            creator=User.objects.get(pk=self.request.user.pk))
        return context


class CountryAdminDashboard(FacultyDashboard):
    '''I guess were are assuming the country the associate themselves
    with is the one they are the admin of? Do we change this in their
    profile update capabilities?'''
    template_name = 'dashboard/icap_dashboard.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(CountryAdminDashboard, self).get_context_data(**kwargs)
        '''Not sure if this is syntactically correct...'''
        country_schools = School.objects.filter(
            country__name=self.object.country)
        context['country_schools'] = country_schools
        return context


class ICAPDashboard(FacultyDashboard):
    template_name = 'dashboard/icap_dashboard.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(ICAPDashboard, self).get_context_data(**kwargs)
        context['pending_teachers'] = PendingTeachers.objects.filter(
            user_profile__profile_type='TE')
        context['countries'] = Country.objects.all()
#             profile_type="ST").count()
#         context['in_progress'] = self.get_students_in_progress()
#         context['incomplete'] = self.get_students_done()
#         context['done'] = self.get_students_incomplete()
        # context['created_groups'] = Group.objects.filter(
        #     creator=User.objects.get(pk=self.request.user.pk))
        # context['joined_groups'] = UserProfile.objects.get(
        #     user=self.request.user.pk).group.all()
        # context['modules'] = Hierarchy.objects.all()
        return context


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
            user_profile.group = Group.objects.filter(
                pk=self.request.POST.__getitem__('group'))
            user_profile.save()
            return self.render_to_json_response(user_profile)
        else:
            return self.request


class JoinGroup(LoggedInMixin, JSONResponseMixin, View):
    template_name = 'dashboard/icap_dashboard.html'

    def post(self, request):
        user_id = request.user.pk
        user_profile = UserProfile.objects.get(user__id=user_id)
        add_group = Group.objects.get(pk=request.POST['group'])
        user_profile.group.add(add_group)
        return self.render_to_json_response({'success': True})


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


class GetSchoolGroups(LoggedInMixin, ListView):
    model = Group
    template_name = 'dashboard/group_list.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        if self.request.is_ajax():
            school_key = self.request.GET.__getitem__('name')
            school = School.objects.get(pk=school_key)
            group_list = Group.objects.filter(school=school)
            return {'group_list': group_list}


class SchoolChoiceView(JSONResponseMixin, View):

    def get(self, *args, **kwargs):
        country_id = kwargs.pop('country_id', None)
        country = get_object_or_404(Country, name=country_id)

        schools = [{'id': '-----', 'name': '-----'}]
        for school in School.objects.filter(country=country):
            schools.append({'id': str(school.id), 'name': school.name})

        return self.render_to_json_response({'schools': schools})


class RegistrationView(FormView):
    '''changing registration view to form'''
    template_name = 'registration/registration_form.html'
    form_class = CreateAccountForm
    success_url = '/account_created/'

    def send_success_email(self, user):
        template = loader.get_template(
            'registration/registration_success_email.txt')

        subject = "ICAP Nursing E-Learning Registration"

        ctx = Context({'user': user})
        message = template.render(ctx)

        sender = settings.NEPI_MAILING_LIST
        recipients = [user.email]
        send_mail(subject, message, sender, recipients)

    def send_teacher_notifiction(self, user):
        template = loader.get_template(
            'registration/faculty_request_email.txt')

        country = dict(COUNTRY_CHOICES)[user.profile.country.name]

        subject = "Nursing E-Learning: Faculty Access Request"

        ctx = Context({'user': user, 'country': country})
        message = template.render(ctx)

        sender = settings.NEPI_MAILING_LIST
        recipients = [settings.ICAP_MAILING_LIST]
        send_mail(subject, message, sender, recipients)

    def form_valid(self, form):
        form_data = form.cleaned_data
        try:
            User.objects.get(username=form_data['username'])
            raise forms.ValidationError("This username already exists")
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

            if 'nepi_affiliated' in form_data:
                new_profile.icap_affil = form_data['nepi_affiliated']

            country = Country.objects.get(name=form_data['country'])
            new_profile.country = country

            new_profile.save()

            # send the user a success email
            if 'email' in form_data:
                self.send_success_email(new_user)

            if 'profile_type' in form_data and form_data['profile_type']:
                PendingTeachers.objects.create(user_profile=new_profile)
                self.send_teacher_notifiction(new_user)

        return super(RegistrationView, self).form_valid(form)


class CreateSchoolView(LoggedInMixin, CreateView):
    '''generic class based view for adding a school'''
    model = School
    template_name = 'icap/add_school.html'
    success_url = '/'


class UpdateSchoolView(LoggedInMixin, UpdateView):
    '''generic class based view for editing a school'''
    model = School
    template_name = 'icap/add_school.html'
    success_url = '/'


class CreateGroupView(LoggedInMixin, CreateView):
    '''generic class based view for
    creating a group'''
    model = Group
    form_class = CreateGroupForm
    template_name = 'dashboard/create_group.html'
    success_url = '/'

    def form_valid(self, request):
        f = CreateGroupForm(self.request.POST)
        new_group = f.save(commit=False)
        creator = User.objects.get(pk=self.request.user.pk)
        profile = UserProfile.objects.get(user=creator)
        school = School.objects.get(pk=profile.school.pk)
        new_group.creator = creator
        new_group.school = school
        new_group.save()
        # why do I need to return an HTTPResponse explicitly?
        # Should happen automatically no?
        return HttpResponseRedirect('/')


class AddGroup(LoggedInMixin, CreateView):
    '''generic class based view for
    creating a group'''
    model = Group
    form_class = CreateGroupForm
    template_name = 'dashboard/new_group.html'
    success_url = '/'

    def form_valid(self, request):
        f = CreateGroupForm(self.request.POST)
        new_group = f.save(commit=False)
        creator = User.objects.get(pk=self.request.user.pk)
        profile = UserProfile.objects.get(user=creator)
        school = School.objects.get(pk=profile.school.pk)
        new_group.creator = creator
        new_group.school = school
        new_group.save()
        # why do I need to return an HTTPResponse explicitly?
        # Should happen automatically no?
        return HttpResponseRedirect('/')


class UpdateGroupView(LoggedInMixin, UpdateView):
    '''generic class based view for
    editing a group'''
    model = Group
    template_name = 'dashboard/create_group.html'
    success_url = '/'
    form_class = CreateGroupForm


class GroupDetail(LoggedInMixin, DetailView):
    '''generic class based view for
    see group details - students etc'''
    model = Group
    template_name = 'dashboard/group_details.html'
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
        context = super(GroupDetail, self).get_context_data(**kwargs)
        context['user_profile'] = UserProfile.objects.get(
            user=self.request.user.pk)
        context['students'] = self.object.userprofile_set.all()
        context['student_count'] = self.object.userprofile_set.all().count()
        context['in_progress'] = self.get_students_in_progress()
        context['incomplete'] = self.get_students_done()
        context['done'] = self.get_students_incomplete()
        return context


class RemoveStudent(LoggedInMixin, JSONResponseMixin, View):
    '''Think this has to be ajax, doing in Django
    is just as much trouble...'''
    template_name = 'dashboard/icap_dashboard.html'

    def post(self, request):
        scenario = get_object_or_404(Group,
                                     pk=request.POST['group'])
        conversation = get_object_or_404(UserProfile,
                                         pk=request.POST['conversation'])
#         conclick = ConvClick.objects.create(conversation=conversation)
#         conclick.save()
        user_profile = UserProfile.objects.get(user__id=request.user.pk)
        leave_group = Group.objects.get(pk=pk)
        leave_group.userprofile_set.remove(user_profile)
        # user_profile.__group_set.remove(leave_group)
        return HttpResponseRedirect("/")


class LeaveGroup(LoggedInMixin, View):
    template_name = 'dashboard/icap_dashboard.html'

    def get(self, request, pk):
        user_profile = UserProfile.objects.get(user__id=request.user.pk)
        leave_group = Group.objects.get(pk=pk)
        leave_group.userprofile_set.remove(user_profile)
        return HttpResponseRedirect("/")


class ContactView(FormView):
    '''changed contact view function to
    generic class based view'''
    template_name = 'main/contact.html'
    form_class = ContactForm
    success_url = '/email_sent/'

    def form_valid(self, form):
        form_data = form.cleaned_data

        sender = form_data['sender']
        subject = form_data['subject']
        message = "First name: %s\nLast name: %s\nMessage: %s" % (
            form_data['first_name'], form_data['last_name'],
            form_data['message'])
        recipients = [settings.NEPI_MAILING_LIST]
        send_mail(subject, message, sender, recipients)
        return super(ContactView, self).form_valid(form)


class DeleteGroupView(LoggedInMixin, DeleteView):
    model = Group
    success_url = reverse_lazy('home')

    def dispatch(self, *args, **kwargs):
        resp = super(DeleteGroupView, self).dispatch(*args, **kwargs)
        if self.request.is_ajax():
            response_data = {"result": "ok"}
            return HttpResponse(json.dumps(response_data),
                                content_type="application/json")
        else:
            # POST request (not ajax) will do a redirect to success_url
            return resp


class StudentClassStatView(LoggedInMixin, DetailView):
    '''This view is for students to see their progress,
    should be included in main base template.'''
    model = Group
    template_name = 'dashboard/view_group.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        students = UserProfile.objects.filter(group__pk=self.object.pk)
        #.exclude(group__created_by=)
        # print students
        # Article.objects.filter(publications__pk=1)
        # .exclude(created_by=userprofile__user)
        return {'object': self.object, 'students': students}
        #  'module': module, 'user': user, 'profile': profile}


class UpdateProfileView(LoggedInMixin, UpdateView):
    model = UserProfile
    template_name = 'dashboard/profile_tab.html'
    form_class = UpdateProfileForm
    success_url = '/'

    def form_valid(self, form):
        form_data = form.cleaned_data
        u_user = User.objects.get(pk=self.request.user.pk)
        u_user.password = form_data['password1']
        u_user.email = form_data['email']
        u_user.first_name = form_data['first_name']
        u_user.last_name = form_data['last_name']
        u_user.save()
        up = UserProfile.objects.get(user=u_user)
        '''IF THIS HAS TO GO IN FORM CLEAN TO KEEP IT
        FROM BLOWING UP - DOES IT NEED TO BE HERE'''
        try:
            up.country = Country.objects.get(
                name=form_data['country'])
            up.save()
        except Country.DoesNotExist:
            new_country = Country.objects.create(name=form_data['country'])
            new_country.save()
            #up.country = new_country
            #up.save()
        if form_data['faculty_access']:
            subject = "Faculty Access Requested"
            message = "The user, " + str(form_data['first_name']) + \
                " " + str(form_data['last_name']) + " from " + \
                str(form_data['country']) + " has requested faculty " + \
                "faculty access.\n\n"
            sender = settings.NEPI_MAILING_LIST
            recipients = [settings.ICAP_MAILING_LIST]
            send_mail(subject, message, sender, recipients)
            pending = PendingTeachers.objects.create(
                user_profile=up)
            pending.save()
        return super(UpdateProfileView, self).form_valid(form)


class GetFacultyCountries(LoggedInMixin, ListView):
    model = Country
    template_name = 'dashboard/faculty_country_list.html'
    success_url = '/'


class GetFacultyCountrySchools(LoggedInMixin, ListView):
    model = School
    template_name = 'dashboard/faculty_school_list.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        if self.request.is_ajax():
            country_key = self.request.GET.__getitem__('name')
            country = Country.objects.get(pk=country_key)
            s = School.objects.filter(country=country)
            return {'school_list': s}
