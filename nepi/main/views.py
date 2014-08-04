'''Views for NEPI, should probably break up
into smaller pieces.'''
from datetime import datetime
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.http.response import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.template import loader
from django.template.context import Context
from django.views.generic import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.views.generic.list import ListView
from nepi.main.choices import COUNTRY_CHOICES
from nepi.main.forms import CreateAccountForm, ContactForm, UpdateProfileForm
from nepi.main.models import Group, UserProfile, Country, School, \
    PendingTeachers
from nepi.mixins import LoggedInMixin, LoggedInMixinSuperuser, \
    LoggedInMixinStaff, JSONResponseMixin, StudentLoggedInMixin, \
    FacultyLoggedInMixin, CountryAdministratorLoggedInMixin, ICAPLoggedInMixin
from pagetree.generic.views import PageView, EditView, InstructorView
from pagetree.models import Hierarchy, UserPageVisit


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
                'disabled': not(previous_unlocked or section.id in visit_ids)
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


class HomeView(LoggedInMixin, View):
    '''redoing so that it simply redirects people where they need to be'''

    def get(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user.pk)
        except UserProfile.DoesNotExist:
            return HttpResponseRedirect(reverse('register'))
        if user_profile.is_student():
            return HttpResponseRedirect(reverse('student-dashboard',
                                        kwargs={'pk': user_profile.pk}))
        elif user_profile.is_teacher():
            return HttpResponseRedirect(reverse('faculty-dashboard',
                                        kwargs={'pk': user_profile.pk}))
        elif user_profile.is_country_administrator():
            return HttpResponseRedirect(reverse('country-dashboard',
                                        kwargs={'pk': user_profile.pk}))
        elif user_profile.is_icap():
            return HttpResponseRedirect(reverse('icap-dashboard',
                                        kwargs={'pk': user_profile.pk}))
        else:
            '''I assume it could be possible another
            app has a profile_type variable?'''
            return HttpResponseRedirect(reverse('register'))


class UserProfileView(DetailView):
    '''For the first tab of the dashboard we are showing
    groups that the user belongs to, and if they do not belong to any
    we are giving the the option to affiliate with one'''
    model = UserProfile
    template_name = 'dashboard/icap_dashboard.html'
    success_url = '/'

    def dispatch(self, *args, **kwargs):
        if int(kwargs.get('pk')) != self.request.user.profile.id:
            return HttpResponseForbidden("forbidden")
        return super(UserProfileView, self).dispatch(*args, **kwargs)

    def get_student_context(self):
        context = {}
        context['hierarchy'] = Hierarchy.objects.get(name='main')
        context['countries'] = COUNTRY_CHOICES
        context['joined_groups'] = self.request.user.profile.joined_groups()
        return context

    def get_faculty_context(self):
        context = self.get_student_context()
        context['created_groups'] = Group.objects.filter(
            creator=self.request.user).exclude(archived=True)
        return context

    def get_country_context(self):
        return self.get_faculty_context()

    def get_icap_context(self):
        context = self.get_country_context()
        context['pending_teachers'] = PendingTeachers.objects.all()
        return context


class StudentDashboard(StudentLoggedInMixin, UserProfileView):

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)
        context.update(self.get_student_context())
        return context


class FacultyDashboard(FacultyLoggedInMixin, UserProfileView):

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)
        context.update(self.get_faculty_context())
        return context

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


class CountryAdminDashboard(CountryAdministratorLoggedInMixin,
                            UserProfileView):

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)
        context.update(self.get_country_context())
        return context


class ICAPDashboard(ICAPLoggedInMixin, UserProfileView):

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)
        context.update(self.get_icap_context())
        return context


class SchoolChoiceView(JSONResponseMixin, View):

    def get(self, *args, **kwargs):
        country_id = kwargs.pop('country_id', None)
        country = get_object_or_404(Country, name=country_id)

        schools = [{'id': '-----', 'name': '-----'}]
        for school in School.objects.filter(country=country):
            schools.append({'id': str(school.id), 'name': school.name})

        return self.render_to_json_response({'schools': schools})


class SchoolGroupChoiceView(LoggedInMixin, JSONResponseMixin, View):

    def get(self, *args, **kwargs):
        school_id = kwargs.pop('school_id', None)
        school = get_object_or_404(School, id=school_id)
        user_groups = self.request.user.profile.group.all()

        available_groups = Group.objects.filter(school=school)
        available_groups = available_groups.exclude(creator=self.request.user)
        available_groups = available_groups.exclude(archived=True)

        groups = []
        for group in available_groups:
            if not group in user_groups:
                groups.append({'id': str(group.id),
                               'name': group.name,
                               'start_date': group.formatted_start_date(),
                               'end_date': group.formatted_end_date(),
                               'creator': group.creator.get_full_name()})

        return self.render_to_json_response({'groups': groups})


class RegistrationView(FormView):
    template_name = 'registration/registration_form.html'
    form_class = CreateAccountForm
    success_url = '/account_created/'

    def send_success_email(self, user):
        if not user.email:
            return

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
                school = get_object_or_404(School, id=form_data['school'])
                PendingTeachers.objects.create(user_profile=new_profile,
                                               school=school)
                self.send_teacher_notifiction(new_user)

        return super(RegistrationView, self).form_valid(form)


class CreateSchoolView(LoggedInMixin, CreateView):
    '''generic class based view for
    adding a school'''
    model = School
    template_name = 'icap/add_school.html'
    success_url = '/'


class UpdateSchoolView(LoggedInMixin, UpdateView):
    '''generic class based view for
    editing a school'''
    model = School
    template_name = 'icap/add_school.html'
    success_url = '/'


class CreateGroupView(LoggedInMixin, View):

    def dispatch(self, *args, **kwargs):
        if self.request.user.profile.is_student():
            return HttpResponseForbidden("forbidden")
        return super(CreateGroupView, self).dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        # validation is taking place client-side
        # @todo -- add server-side validation & then client-side error msg
        # just in case javascript is turned off

        # dates come in as MM/DD/YYYY
        start_date = self.request.POST.get('start_date')
        end_date = self.request.POST.get('end_date')
        fmt = "%m/%d/%Y"

        group = Group()
        group.start_date = datetime.strptime(start_date, fmt).date()
        group.end_date = datetime.strptime(end_date, fmt).date()
        group.name = self.request.POST.get('name')

        module_name = self.request.POST.get('module')
        group.module = Hierarchy.objects.get(name=module_name)

        group.creator = self.request.user
        group.school = self.request.user.profile.school
        group.save()

        url = '/%s-dashboard/%s/#user-groups' % (
            self.request.user.profile.role(),
            self.request.user.profile.id)
        return HttpResponseRedirect(url)


class UpdateGroupView(LoggedInMixin, View):
    def post(self, *args, **kwargs):
        pk = self.request.POST.get('pk')
        group = get_object_or_404(Group, pk=pk)

        if group.creator != self.request.user:
            return HttpResponseForbidden(
                'You are not authorized to update this group')
        start_date = self.request.POST.get('start_date')
        end_date = self.request.POST.get('end_date')
        fmt = "%m/%d/%Y"

        group.start_date = datetime.strptime(start_date, fmt).date()
        group.end_date = datetime.strptime(end_date, fmt).date()
        group.name = self.request.POST.get('name')
        group.save()

        url = '/%s-dashboard/%s/#user-groups' % (
            self.request.user.profile.role(),
            self.request.user.profile.id)
        return HttpResponseRedirect(url)


class JoinGroup(LoggedInMixin, View):
    template_name = 'dashboard/icap_dashboard.html'

    def post(self, request):
        group = get_object_or_404(Group, pk=request.POST.get('group'))
        request.user.profile.group.add(group)

        url = '/%s-dashboard/%s/#user-groups' % (request.user.profile.role(),
                                                 request.user.profile.id)
        return HttpResponseRedirect(url)


class DeleteGroupView(LoggedInMixin, JSONResponseMixin, View):

    def post(self, *args, **kwargs):
        group = get_object_or_404(Group, pk=self.request.POST.get('group'))
        if not group.creator == self.request.user:
            return HttpResponseForbidden(
                'You are not authorized to delete this group')
        group.delete()
        return self.render_to_json_response({'success': True})


class ArchiveGroupView(LoggedInMixin, JSONResponseMixin, View):

    def post(self, *args, **kwargs):
        group = get_object_or_404(Group, pk=self.request.POST.get('group'))
        if not group.creator == self.request.user:
            return HttpResponseForbidden(
                'You are not authorized to archive this group')
        group.archived = True
        group.save()
        return self.render_to_json_response({'success': True})


class LeaveGroup(LoggedInMixin, JSONResponseMixin, View):

    def post(self, *args, **kwargs):
        group = get_object_or_404(Group, pk=self.request.POST.get('group'))
        self.request.user.profile.group.remove(group)
        return self.render_to_json_response({'success': True})


class ConfirmFacultyView(LoggedInMixin, JSONResponseMixin, View):

    def send_confirmation_email(self, user):
        template = loader.get_template(
            'dashboard/faculty_success_email.txt')

        subject = "ICAP Nursing E-Learning Faculty Access"

        ctx = Context({'user': user})
        message = template.render(ctx)

        sender = settings.NEPI_MAILING_LIST
        send_mail(subject, message, sender, [user.email])

    def post(self, *args, **kwargs):
        if not (self.request.user.profile.is_icap() or
                self.request.user.profile.is_country_administrator()):
            return HttpResponseForbidden(
                'You are not authorized to deny faculty access.')

        user = get_object_or_404(User, pk=self.request.POST.get('user_id'))

        pending = PendingTeachers.objects.get(user_profile=user.profile)

        user.profile.school = pending.school
        user.profile.country = pending.school.country
        user.profile.profile_type = 'TE'
        user.profile.save()
        self.send_confirmation_email(user)

        pending.delete()
        return self.render_to_json_response({'success': True})


class DenyFacultyView(LoggedInMixin, JSONResponseMixin, View):

    def send_denied_email(self, user, school):
        template = loader.get_template(
            'dashboard/faculty_denied_email.txt')

        subject = "ICAP Nursing E-Learning Faculty Access"

        ctx = Context({'user': user, 'school': school})
        message = template.render(ctx)

        sender = settings.NEPI_MAILING_LIST
        send_mail(subject, message, sender, [user.email])

    def post(self, *args, **kwargs):
        if not (self.request.user.profile.is_icap() or
                self.request.user.profile.is_country_administrator()):
            return HttpResponseForbidden(
                'You are not authorized to deny faculty access.')

        user = get_object_or_404(User, pk=self.request.POST.get('user_id'))
        pending = PendingTeachers.objects.get(user_profile=user.profile)

        self.send_denied_email(user, pending.school)

        pending.delete()
        return self.render_to_json_response({'success': True})


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
    template_name = 'dashboard/view_group.html'

    '''Remove the student from a course.'''
    def post(self, request):
        group = get_object_or_404(Group,
                                  pk=request.POST['group'])
        student = get_object_or_404(UserProfile,
                                    pk=request.POST['student'])
        group.userprofile_set.remove(student)
        return self.render_to_json_response({'success': True})


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


class StudentClassStatView(LoggedInMixin, DetailView):
    '''This view is for students to see their progress,
    should be included in main base template.'''
    model = Group
    template_name = 'view_group_stats.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        if self.request.is_ajax():
            module = self.group.__module
            user = User.objects.get(pk=self.request.user.pk)
            profile = UserProfile.objects.get(user=user)
            return {'module': module, 'user': user, 'profile': profile}


class UpdateProfileView(LoggedInMixin, UpdateView):
    model = UserProfile
    template_name = 'dashboard/profile_tab.html'
    form_class = UpdateProfileForm
    success_url = '/'

    def form_valid(self, form):
        # response = super(UpdateProfileView, self).form_valid(form)
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
