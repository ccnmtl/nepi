import csv
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.core.mail import send_mail
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect
from django.http.response import HttpResponseForbidden, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.template import loader
from django.urls.base import reverse
from django.utils import translation
from django.views.generic import View
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView
from pagetree.generic.views import PageView, EditView
from pagetree.helpers import get_section_from_path
from pagetree.models import Hierarchy, UserPageVisit
from waffle import flag_is_active

from nepi.main.forms import CreateAccountForm, ContactForm, UpdateProfileForm
from nepi.main.models import Group, UserProfile, Country, School, \
    PendingTeachers, DetailedReport, PROFILE_CHOICES, HierarchyCache, \
    LearningModule
from nepi.main.templatetags.progressreport import get_progress_report, \
    average_quiz_score, satisfaction_rating, completed
from nepi.mixins import (
    LoggedInMixin, JSONResponseMixin, AdministrationOnlyMixin,
    IcapAdministrationOnlyMixin, InitializeHierarchyMixin, LoggedInMixinStaff)
LANGUAGE_SESSION_KEY = '_language'


# Set the user's language on login & profile update
def set_session_language(sender, user, request, **kwargs):
    try:
        translation.activate(user.profile.language)
        request.session[LANGUAGE_SESSION_KEY] = user.profile.language
    except UserProfile.DoesNotExist:
        pass  # uni user logged in with no profile


user_logged_in.connect(set_session_language)


def context_processor(request):
    return dict(
        hierarchies=Hierarchy.objects.all(), MEDIA_URL=settings.MEDIA_URL)


class NepiDeprecatedPageView(LoggedInMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        path = kwargs.get('path')
        hierarchy = Hierarchy.objects.get(name='optionb-en')

        section = get_section_from_path(
            path,
            hierarchy_name=hierarchy.name,
            hierarchy_base=hierarchy.base_url)

        return section.get_absolute_url()


class NepiPageView(LoggedInMixin, InitializeHierarchyMixin, PageView):
    template_name = "main/page.html"
    gated = True

    def get_extra_context(self):
        menu = []
        visits = UserPageVisit.objects.filter(user=self.request.user,
                                              status='complete')
        visit_ids = visits.values_list('section__id', flat=True)

        previous_unlocked = True
        for section in HierarchyCache.get_descendants(self.root):
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


class NepiEditView(LoggedInMixinStaff, InitializeHierarchyMixin, EditView):
    template_name = "pagetree/edit_page.html"

    def get_context_data(self, path):
        ctx = super(NepiEditView, self).get_context_data(path)

        edit_flag = '%s-edit' % self.hierarchy_name
        ctx['editable'] = flag_is_active(self.request, edit_flag)
        return ctx


class HomeView(LoggedInMixin, View):
    '''redoing so that it simply redirects people where they need to be'''

    def get(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user.pk)
        except UserProfile.DoesNotExist:
            return HttpResponseRedirect(reverse('register'))

        if user_profile.is_student():
            url = '/dashboard/#user-modules'
        else:
            url = '/dashboard/#user-groups'

        return HttpResponseRedirect(url)


class RegistrationView(FormView):
    template_name = 'registration/registration_form.html'
    form_class = CreateAccountForm
    success_url = '/account_created/'

    def form_valid(self, form):
        form.save()
        return super(RegistrationView, self).form_valid(form)


class UserProfileView(LoggedInMixin, DetailView):
    '''For the groups tab of the dashboard we are showing
    groups that the user belongs to, and if they do not belong to any
    we are giving the the option to affiliate with one'''
    model = UserProfile
    template_name = 'dashboard/dashboard.html'
    success_url = '/'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_student_context(self, hierarchy):
        context = {}
        context['optionb_progress_report'] = get_progress_report(
            [self.request.user], hierarchy)
        return context

    def get_faculty_context(self):
        context = {}

        groups = self.request.user.profile.get_managed_groups()
        context['managed_groups'] = groups
        return context

    def get_institution_context(self):
        context = {}

        groups = self.request.user.profile.get_managed_groups()
        context['managed_groups'] = groups

        teachers = PendingTeachers.objects.filter(
            Q(school=self.request.user.profile.school))
        teachers = teachers.order_by('school__name')
        context['pending_teachers'] = teachers
        return context

    def get_country_context(self):
        context = {}

        groups = self.request.user.profile.get_managed_groups()
        context['managed_groups'] = groups

        teachers = PendingTeachers.objects.filter(
            Q(school__country=self.request.user.profile.country))
        teachers = teachers.order_by('school__name')
        context['pending_teachers'] = teachers

        return context

    def get_icap_context(self):
        context = {}

        groups = self.request.user.profile.get_managed_groups()
        context['managed_groups'] = groups

        teachers = PendingTeachers.objects.all()
        teachers = teachers.order_by('school__country__display_name',
                                     'school__name')
        context['pending_teachers'] = teachers
        return context

    def get_context_data(self, **kwargs):
        profile = self.request.user.profile
        context = super(UserProfileView, self).get_context_data(**kwargs)

        hierarchy_name = 'optionb-%s' % profile.language
        hierarchy = Hierarchy.objects.get(name=hierarchy_name)
        context['optionb'] = hierarchy

        context['profile_form'] = UpdateProfileForm(instance=self.request.user)
        context['countries'] = Country.choices()
        context['joined_groups'] = self.request.user.profile.joined_groups()

        if profile.is_student():
            context.update(self.get_student_context(hierarchy))
        elif profile.is_teacher():
            context.update(self.get_faculty_context())
        elif profile.is_institution_administrator():
            context.update(self.get_institution_context())
        elif profile.is_country_administrator():
            context.update(self.get_country_context())
        elif profile.is_icap():
            context.update(self.get_icap_context())

        return context

    def maybe_activate_language(self, form):
        language = form.cleaned_data.get('language', settings.DEFAULT_LANGUAGE)

        if self.request.user.profile.language != language:
            self.request.user.profile.refresh_from_db()
            set_session_language(None, self.request.user, self.request)

    def post(self, *args, **kwargs):
        self.object = self.get_object()

        profile_form = UpdateProfileForm(self.request.POST)

        if profile_form.is_valid():
            profile_form.save()
            messages.add_message(self.request, messages.INFO,
                                 'Your changes have been saved.')

            self.maybe_activate_language(profile_form)

            return HttpResponseRedirect('/dashboard/#user-profile')
        else:
            context = self.get_context_data(object=self.object)
            context['profile_form'] = profile_form
            return self.render_to_response(context)


class ConfirmLanguageView(LoggedInMixin, TemplateView):
    template_name = "main/confirm_language.html"

    def get_context_data(self, **kwargs):
        optionb = LearningModule.get_hierarchy_for_language(
            'optionb', self.request.user.profile.language)
        return {
            'user': self.request.user,
            'next': optionb.get_root().get_absolute_url(),
            'available_languages': settings.LANGUAGES
        }

    def post(self, *args, **kwargs):
        language = self.request.POST.get('language', settings.DEFAULT_LANGUAGE)

        if self.request.user.profile.language != language:
            self.request.user.profile.language = language
            self.request.user.profile.save()
            set_session_language(None, self.request.user, self.request)

        hierarchy = LearningModule.get_hierarchy_for_language('optionb',
                                                              language)
        return HttpResponseRedirect(hierarchy.get_root().get_absolute_url())


class ReportView(LoggedInMixin, AdministrationOnlyMixin, TemplateView):
    template_name = "dashboard/reports.html"

    def get_context_data(self, **kwargs):
        return {
            'user': self.request.user,
            'countries': Country.choices()
        }


class PeopleView(LoggedInMixin, IcapAdministrationOnlyMixin, TemplateView):
    template_name = "dashboard/people.html"

    def get_context_data(self, **kwargs):
        return {
            'user': self.request.user,
            'countries': Country.choices(),
            'roles': PROFILE_CHOICES
        }


class PeopleFilterView(LoggedInMixin, IcapAdministrationOnlyMixin,
                       JSONResponseMixin, View):

    MAX_PEOPLE = 40

    def serialize_participants(self, participants):
        the_json = []
        for participant in participants:
            values = {
                'last_name': participant.user.last_name,
                'first_name': participant.user.first_name,
                'role': participant.role(),
                'email': participant.user.email
            }

            if participant.school:
                values['school'] = participant.school.name
                values['country'] = participant.country.display_name
            if participant.country:
                values['country'] = participant.country.display_name

            the_json.append(values)
        return the_json

    def filter(self):
        participants = UserProfile.objects.all()

        profile_type = self.request.GET.get('role', 'all')
        if profile_type != 'all':
            participants = participants.filter(profile_type=profile_type)

        country_id = self.request.GET.get('country', 'all')
        if country_id != 'all':
            participants = participants.filter(
                Q(country__name=country_id))

        school_id = self.request.GET.get('school', 'all')
        if school_id == 'unaffiliated':
            participants = participants.filter(school__isnull=True)
        elif school_id != 'all':
            participants = participants.filter(Q(school__id=school_id))

        participants = participants.order_by(
            'user__last_name', 'user__first_name')

        return participants

    def get(self, *args, **kwargs):
        participants = self.filter()

        # slice the list
        offset = int(self.request.GET.get('offset', 0))
        the_page = participants[offset:offset + self.MAX_PEOPLE]

        return self.render_to_json_response({
            'offset': offset,
            'total': participants.count(),
            'count': len(the_page),
            'limit': self.MAX_PEOPLE,
            'participants': self.serialize_participants(the_page),
        })


class SchoolChoiceView(JSONResponseMixin, View):

    def get(self, *args, **kwargs):
        country_id = kwargs.pop('country_id', None)
        country = get_object_or_404(Country, name=country_id)

        schools = []
        for school in School.objects.filter(country=country):
            schools.append({'id': str(school.id), 'name': school.name})

        return self.render_to_json_response({'schools': schools})


class SchoolGroupChoiceView(LoggedInMixin, JSONResponseMixin, View):

    def post(self, *args, **kwargs):
        school_id = kwargs.pop('school_id', None)
        school = get_object_or_404(School, id=school_id)

        if self.request.POST.get('managed', False):
            groups = self.request.user.profile.get_managed_groups()
        else:
            user_groups = self.request.user.profile.group.all()
            groups = Group.objects.all().exclude(id__in=user_groups)
            groups = groups.exclude(creator=self.request.user)
            groups = groups.exclude(archived=True)

        groups = groups.filter(school=school)

        visible_groups = []
        for group in groups:
            visible_groups.append({'id': str(group.id),
                                   'name': group.name,
                                   'start_date': group.formatted_start_date(),
                                   'end_date': group.formatted_end_date(),
                                   'creator': group.creator.get_full_name()})

        return self.render_to_json_response({'groups': visible_groups})


class CreateSchoolView(LoggedInMixin, AdministrationOnlyMixin, CreateView):
    '''generic class based view for adding a school'''
    model = School
    template_name = 'icap/add_school.html'
    success_url = '/'
    fields = ['country', 'name']


class UpdateSchoolView(LoggedInMixin, AdministrationOnlyMixin, UpdateView):
    '''generic class based view for editing a school'''
    model = School
    template_name = 'icap/add_school.html'
    success_url = '/'
    fields = ['country', 'name']


class CreateGroupView(LoggedInMixin, AdministrationOnlyMixin, View):

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
        if (self.request.user.profile.is_teacher() or
                self.request.user.profile.is_institution_administrator()):
            group.school = self.request.user.profile.school
        else:
            school = School.objects.get(id=self.request.POST.get('school'))
            group.school = school

        group.save()

        return HttpResponseRedirect('/dashboard/#user-groups')


class UpdateGroupView(LoggedInMixin, AdministrationOnlyMixin, View):

    def post(self, *args, **kwargs):
        pk = self.request.POST.get('pk')
        group = get_object_or_404(Group, pk=pk)

        if (self.request.user.profile.is_teacher() and
                not group.creator == self.request.user):
            return HttpResponseForbidden(
                'You are not authorized to update this group')
        start_date = self.request.POST.get('start_date')
        end_date = self.request.POST.get('end_date')
        fmt = "%m/%d/%Y"

        group.start_date = datetime.strptime(start_date, fmt).date()
        group.end_date = datetime.strptime(end_date, fmt).date()
        group.name = self.request.POST.get('name')
        group.save()

        return HttpResponseRedirect('/dashboard/#user-groups')


class JoinGroup(LoggedInMixin, View):

    def post(self, request):
        group = get_object_or_404(Group, pk=request.POST.get('group'))
        request.user.profile.group.add(group)

        return HttpResponseRedirect('/dashboard/#user-groups')


class DeleteGroupView(LoggedInMixin, AdministrationOnlyMixin,
                      JSONResponseMixin, View):

    def post(self, *args, **kwargs):
        group = get_object_or_404(Group, pk=self.request.POST.get('group'))
        if (self.request.user.profile.is_teacher() and
                not group.creator == self.request.user):
            return HttpResponseForbidden(
                'You are not authorized to delete this group')
        group.delete()
        return self.render_to_json_response({'success': True})


class ArchiveGroupView(LoggedInMixin, AdministrationOnlyMixin,
                       JSONResponseMixin, View):

    def post(self, *args, **kwargs):
        group = get_object_or_404(Group, pk=self.request.POST.get('group'))
        if (self.request.user.profile.is_student() or
            (self.request.user.profile.is_teacher() and
             not group.creator == self.request.user)):
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


class AddUserToGroup(LoggedInMixin, IcapAdministrationOnlyMixin, View):

    '''Add one or more users to a group.'''
    def post(self, request):
        group_id = request.POST.get('group', None)
        group = get_object_or_404(Group, pk=group_id)

        errors = []
        usernames = request.POST.get('usernames', '').split('\n')
        for username in usernames:
            username = username.strip()
            try:
                user = User.objects.get(username=username)
                user.profile.group.add(group)
            except User.DoesNotExist:
                errors.append(username)
                pass  # username does not exist

        messages.add_message(
            request, messages.INFO,
            'Added %s user(s)' % str(len(usernames) - len(errors)))

        if len(errors) > 0:
            messages.add_message(
                request, messages.ERROR,
                'Some usernames could not be found: %s' % ", ".join(errors))

        return HttpResponseRedirect(
            reverse('roster-details', kwargs={'pk': group_id}))


class ConfirmFacultyView(LoggedInMixin, AdministrationOnlyMixin,
                         JSONResponseMixin, View):

    def send_confirmation_email(self, user):
        template = loader.get_template(
            'dashboard/faculty_success_email.txt')

        subject = "Your request for faculty access to the " \
            "ICAP Nursing E-learning system has been approved"

        ctx = {'user': user, 'school': user.profile.school}
        message = template.render(ctx)

        sender = settings.NEPI_MAILING_LIST
        send_mail(subject, message, sender, [user.email])

    def post(self, *args, **kwargs):
        if not (self.request.user.profile.is_icap() or
                self.request.user.profile.is_country_administrator() or
                self.request.user.profile.is_institution_administrator()):
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


class DenyFacultyView(LoggedInMixin, AdministrationOnlyMixin,
                      JSONResponseMixin, View):

    def send_denied_email(self, user, school):
        template = loader.get_template(
            'dashboard/faculty_denied_email.txt')

        subject = "Your request for faculty access to the "\
            "ICAP Nursing E-learning system has been denied"

        message = template.render({'user': user, 'school': school})

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


class RemoveStudent(LoggedInMixin, AdministrationOnlyMixin,
                    JSONResponseMixin, View):

    '''Remove the student from a course.'''
    def post(self, request):
        group = get_object_or_404(Group,
                                  pk=request.POST['group'])
        student = get_object_or_404(UserProfile,
                                    pk=request.POST['student'])
        group.userprofile_set.remove(student)
        return self.render_to_json_response({'success': True})


class ContactView(FormView):
    '''changed contact view function to generic class based view'''
    template_name = 'main/contact.html'
    form_class = ContactForm
    success_url = '/email_sent/'

    def form_valid(self, form):
        form.cleaned_data['user'] = self.request.user
        ctx = form.cleaned_data

        template = loader.get_template('dashboard/contact_us_email.txt')
        message = template.render(ctx)

        sender = settings.NEPI_MAILING_LIST
        subject = "ICAP Nursing E-learning message: %s" % ctx['subject']
        recipients = [settings.ICAP_MAILING_LIST]
        send_mail(subject, message, sender, recipients)
        return super(ContactView, self).form_valid(form)


class BaseReportMixin(object):

    all = 'all'
    unaffiliated = 'unaffiliated'

    def get_country_criteria(self, request):
        country_name = None
        country_id = request.POST.get('country', None)
        if country_id == 'all':
            country_name = "All Countries"
        else:
            try:
                country = Country.objects.get(name=country_id)
                country_name = country.display_name
            except (Country.DoesNotExist, ValueError):
                pass

        return country_name

    def get_school_criteria(self, request):
        school_name = None
        school_id = request.POST.get('school', None)
        if school_id == "all":
            school_name = "All Institutions"
        elif school_id == "unaffiliated":
            school_name = "Unaffiliated Students"
        else:
            try:
                school = School.objects.get(id=school_id)
                school_name = school.name
            except (School.DoesNotExist, ValueError):
                pass

        return school_name

    def get_group_criteria(self, request):
        group_name = None
        group_id = request.POST.get('schoolgroup', None)
        if group_id == 'all':
            group_name = 'All Groups'
        else:
            try:
                group = Group.objects.get(id=group_id)
                group_name = group.name
            except (Group.DoesNotExist, ValueError):
                pass

        return group_name

    def filter_by_country(self, groups, country_name):
        if country_name != self.all:
            groups = groups.filter(school__country__name=country_name)
        return groups

    def filter_by_school(self, groups, school_id):
        if school_id != self.all and school_id != self.unaffiliated:
            groups = groups.filter(school__id=school_id)
        return groups

    def filter_by_creator(self, groups, user):
        # Teachers can only see their own groups
        if user.profile.is_teacher():
            groups = groups.filter(creator=user)
        return groups

    def get_country_and_school(self, request):
        profile = request.user.profile

        if profile.is_teacher() or profile.is_institution_administrator():
            country_name = profile.school.country.name
            school_id = profile.school.id
        elif profile.is_country_administrator():
            country_name = profile.country.name
            school_id = request.POST.get('school', self.all)
        else:
            country_name = request.POST.get('country', self.all)
            school_id = request.POST.get('school', self.all)

        return (country_name, school_id)

    def get_users_and_groups(self, request, hierarchy):
        group_id = request.POST.get('schoolgroup', self.all)
        (country_name, school_id) = self.get_country_and_school(request)
        groups = None
        users = User.objects.none()

        if group_id != self.all:  # requesting a single group
            groups = Group.objects.filter(id=group_id)
        elif country_name == self.all:  # all users in all countries
            users = User.objects.all()
        elif school_id == self.unaffiliated:  # all solo users in country
            users = User.objects.filter(profile__country__name=country_name,
                                        profile__group=None)
        else:  # group based queries
            groups = Group.objects.filter(archived=False, module=hierarchy)
            groups = self.filter_by_country(groups, country_name)
            groups = self.filter_by_school(groups, school_id)
            groups = self.filter_by_creator(groups, request.user)

        if groups:
            users = User.objects.filter(profile__group__in=groups)
        else:
            # just include users who have visited the selected hierarchy
            upv = UserPageVisit.objects.filter(section__hierarchy=hierarchy)
            user_ids = upv.values_list('user_id', flat=True).distinct()
            users = users.filter(id__in=user_ids)

        if users:
            users = users.filter(profile__profile_type='ST').distinct()

        return (users, groups)

    def percent_complete(self, user, sections):
        visits = UserPageVisit.objects.filter(user=user,
                                              section__in=sections)
        return len(visits) / float(len(sections)) * 100

    def classify_group_users(self, groups, hierarchy, sections):
        ctx = {'total': 0, 'completed': 0, 'completed_users': [],
               'incomplete': 0, 'inprogress': 0}
        users = []

        for group in groups:
            active = group.is_active()
            for profile in group.students():
                if profile.user.username not in users:
                    ctx['total'] += 1

                    if completed(profile.user, hierarchy):
                        ctx['completed'] += 1
                        ctx['completed_users'].append(profile.user)
                    elif self.percent_complete(profile.user, sections) > 0:
                        if active:
                            ctx['inprogress'] += 1
                        else:
                            ctx['incomplete'] += 1
                    users.append(profile.user.username)
        return ctx

    def classify_unaffiliated_users(self, users, hierarchy, sections):
        ctx = {'total': 0, 'completed': 0, 'completed_users': [],
               'incomplete': 0, 'inprogress': 0}

        for user in users:
            ctx['total'] += 1
            if completed(user, hierarchy):
                ctx['completed'] += 1
                ctx['completed_users'].append(user)
            elif self.percent_complete(user, sections) > 0:
                ctx['inprogress'] += 1

        return ctx


class GroupDetail(LoggedInMixin, AdministrationOnlyMixin,
                  BaseReportMixin, DetailView):
    '''Group Progress Report'''
    model = Group
    template_name = 'dashboard/group_details.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        ctx = super(GroupDetail, self).get_context_data(**kwargs)
        ctx['stats'] = []

        module_name = LearningModule.get_module_name(self.object.module)
        for h in LearningModule.get_hierarchies_for_module(module_name):
            sections = HierarchyCache.get_descendant_ids(h.get_root())
            stat = self.classify_group_users([self.object], h, sections)
            stat['language'] = LearningModule.get_module_language(h)
            stat['hierarchy'] = h
            ctx['stats'].append(stat)

        return ctx


class RosterDetail(LoggedInMixin, AdministrationOnlyMixin,
                   BaseReportMixin, DetailView):
    '''Student roster. add/remove students, individual progress links'''
    model = Group
    template_name = 'dashboard/roster_details.html'
    success_url = '/'


class StudentGroupDetail(LoggedInMixin, AdministrationOnlyMixin, TemplateView):
    '''Student Progress Report'''
    model = User
    template_name = 'dashboard/student_details.html'

    def get_context_data(self, **kwargs):
        context = super(StudentGroupDetail, self).get_context_data(**kwargs)
        group = get_object_or_404(Group, id=kwargs.get('group_id'))
        user = get_object_or_404(User, id=kwargs.get('student_id'))

        module_name = LearningModule.get_module_name(group.module)
        user_hierarchy = LearningModule.get_hierarchy_for_language(
            module_name, user.profile.language)

        context['group'] = group
        context['student'] = user
        context['progress_report'] = get_progress_report([user],
                                                         user_hierarchy)
        return context


class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


class DownloadableReportView(LoggedInMixin, AdministrationOnlyMixin,
                             BaseReportMixin, View):

    def get_detailed_report_keys(self, hierarchies):
        report = DetailedReport(hierarchies[0], None)
        return report.metadata(hierarchies)

    def get_detailed_report_values(self, hierarchies, users):
        the_hierarchy = hierarchies.first()

        report = DetailedReport(the_hierarchy, users)
        return report.values(hierarchies)

    def get_aggregate_report(self, request, hierarchy, users, groups):
        sections = HierarchyCache.get_descendant_ids(hierarchy.get_root())

        if groups is None:  # reporting on unaffiliated users
            ctx = self.classify_unaffiliated_users(users, hierarchy, sections)
        else:
            ctx = self.classify_group_users(groups, hierarchy, sections)

        yield ['CRITERIA']
        yield ['Country', 'Institution', 'Group', 'Total Members']
        yield [self.get_country_criteria(request),
               self.get_school_criteria(request),
               self.get_group_criteria(request), len(users)]
        yield ['']
        yield ['LANGUAGE']
        yield [LearningModule.get_module_language(hierarchy)]
        yield ['']
        yield ['STUDENT PROGRESS']
        yield ['Completed', 'Incomplete', 'In Progress']
        yield [ctx['completed'], ctx['incomplete'], ctx['inprogress']]

        if ctx['completed'] > 0:
            yield ['']
            users = ctx['completed_users']
            yield ['COMPLETED USER AVERAGES']
            yield ['Completed', ctx['completed']]

            pretest = average_quiz_score(users, hierarchy, 'pretest')
            yield ['Pre-test Score', pretest]

            posttest = average_quiz_score(users, hierarchy, 'posttest')
            yield ['Post-test Score', posttest]

            change = None
            if (pretest is not None and pretest >= 0 and
                    posttest is not None and posttest >= 0):
                change = posttest - pretest
            yield ['Pre/Post Change', change]

            yield ['Satisfaction Score', satisfaction_rating(users, hierarchy)]

    def post(self, request):
        hierarchy_name = request.POST.get('module', 'optionb-en')
        hierarchies = Hierarchy.objects.filter(name=hierarchy_name)
        hierarchy = hierarchies[0]

        users, groups = self.get_users_and_groups(request, hierarchy)

        report_type = request.POST.get('report-type', 'keys')
        if report_type == 'aggregate':
            rows = self.get_aggregate_report(request, hierarchy, users, groups)
        elif report_type == 'values':
            rows = self.get_detailed_report_values(hierarchies, users)
        else:
            rows = self.get_detailed_report_keys(hierarchies)

        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)

        fnm = "optionb_%s.csv" % report_type
        response = StreamingHttpResponse(
            (writer.writerow(row) for row in rows), content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="' + fnm + '"'
        return response
