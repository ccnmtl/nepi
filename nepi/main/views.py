from StringIO import StringIO
import csv
from datetime import datetime
from zipfile import ZipFile

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.http.response import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.template import loader
from django.template.context import Context
from django.views.generic import View
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView
from pagetree.generic.views import PageView, EditView, InstructorView
from pagetree.models import Hierarchy, UserPageVisit

from nepi.main.forms import CreateAccountForm, ContactForm, UpdateProfileForm
from nepi.main.models import Group, UserProfile, Country, School, \
    PendingTeachers, DetailedReport, PROFILE_CHOICES
from nepi.main.templatetags.progressreport import get_progress_report
from nepi.mixins import LoggedInMixin, LoggedInMixinSuperuser, \
    LoggedInMixinStaff, JSONResponseMixin, AdministrationOnlyMixin, \
    IcapAdministrationOnlyMixin


class ViewPage(LoggedInMixin, PageView):
    template_name = "main/page.html"
    hierarchy_name = "main"
    hierarchy_base = "/pages/main/"
    gated = True

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
    '''For the first tab of the dashboard we are showing
    groups that the user belongs to, and if they do not belong to any
    we are giving the the option to affiliate with one'''
    model = UserProfile
    template_name = 'dashboard/dashboard.html'
    success_url = '/'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_student_context(self):
        context = {}
        hierarchy = Hierarchy.objects.get(name='main')
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
        context = super(UserProfileView, self).get_context_data(**kwargs)

        # todo - this will require some addition when new modules are added
        hierarchy = Hierarchy.objects.get(name='main')
        context['optionb'] = hierarchy

        context['profile_form'] = UpdateProfileForm(instance=self.request.user)
        context['countries'] = Country.choices()
        context['joined_groups'] = self.request.user.profile.joined_groups()

        if self.request.user.profile.is_student():
            context.update(self.get_student_context())
        elif self.request.user.profile.is_teacher():
            context.update(self.get_faculty_context())
        elif self.request.user.profile.is_institution_administrator():
            context.update(self.get_institution_context())
        elif self.request.user.profile.is_country_administrator():
            context.update(self.get_country_context())
        elif self.request.user.profile.is_icap():
            context.update(self.get_icap_context())

        return context

    def post(self, *args, **kwargs):
        self.object = self.get_object()

        profile_form = UpdateProfileForm(self.request.POST)

        if profile_form.is_valid():
            profile_form.save()
            messages.add_message(self.request, messages.INFO,
                                 'Your changes have been saved.')

            return HttpResponseRedirect('/dashboard/#user-profile')

        context = self.get_context_data(object=self.object)
        context['profile_form'] = profile_form
        return self.render_to_response(context)


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


class UpdateSchoolView(LoggedInMixin, AdministrationOnlyMixin, UpdateView):
    '''generic class based view for editing a school'''
    model = School
    template_name = 'icap/add_school.html'
    success_url = '/'


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

        if (self.request.user.profile.is_student() or
            (self.request.user.profile.is_teacher() and
             not group.creator == self.request.user)):
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
    template_name = 'dashboard/dashboard.html'

    def post(self, request):
        group = get_object_or_404(Group, pk=request.POST.get('group'))
        request.user.profile.group.add(group)

        return HttpResponseRedirect('/dashboard/#user-groups')


class DeleteGroupView(LoggedInMixin, AdministrationOnlyMixin,
                      JSONResponseMixin, View):

    def post(self, *args, **kwargs):
        group = get_object_or_404(Group, pk=self.request.POST.get('group'))
        if (self.request.user.profile.is_student() or
            (self.request.user.profile.is_teacher() and
             not group.creator == self.request.user)):
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


class ConfirmFacultyView(LoggedInMixin, AdministrationOnlyMixin,
                         JSONResponseMixin, View):

    def send_confirmation_email(self, user):
        template = loader.get_template(
            'dashboard/faculty_success_email.txt')

        subject = "Your request for faculty access to the " \
            "ICAP Nursing E-learning system has been approved"

        ctx = Context({'user': user, 'school': user.profile.school})
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
        form_data = form.cleaned_data

        sender = settings.NEPI_MAILING_LIST
        subject = "ICAP Nursing E-learning message: %s" % form_data['subject']
        message = "From: %s %s\n\nMessage: %s\n\nReply to: %s" % (
            form_data['first_name'], form_data['last_name'],
            form_data['message'], form_data['sender'])
        recipients = [settings.ICAP_MAILING_LIST]
        send_mail(subject, message, sender, recipients)
        return super(ContactView, self).form_valid(form)


class BaseReportMixin():

    all = 'all'
    unaffiliated = 'unaffiliated'

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
        users = None

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

        if users:
            users = users.filter(profile__profile_type='ST').distinct()

        return (users, groups)

    def percent_complete(self, user, sections):
        visits = UserPageVisit.objects.filter(user=user,
                                              section__in=sections)
        return len(visits) / float(len(sections)) * 100

    def classify_group_users(self, groups, sections):
        ctx = {'total': 0, 'completed': 0, 'completed_users': [],
               'incomplete': 0, 'inprogress': 0}

        for group in groups:
            active = group.is_active()
            for profile in group.students():
                ctx['total'] += 1
                pct = self.percent_complete(profile.user, sections)
                if pct == 100:
                    ctx['completed'] += 1
                    ctx['completed_users'].append(profile.user)
                elif pct > 0:
                    if active:
                        ctx['inprogress'] += 1
                    else:
                        ctx['incomplete'] += 1
        return ctx

    def classify_unaffiliated_users(self, users, sections):
        ctx = {'total': 0, 'completed': 0, 'completed_users': [],
               'incomplete': 0, 'inprogress': 0}

        for user in users:
            ctx['total'] += 1
            pct = self.percent_complete(user, sections)
            if pct == 100:
                ctx['completed'] += 1
                ctx['completed_users'].append(user)
            elif pct > 0:
                ctx['inprogress'] += 1

        return ctx


class GroupDetail(LoggedInMixin, AdministrationOnlyMixin,
                  BaseReportMixin, DetailView):
    '''generic class based view for
    see group details - student roster. add/remove students etc'''
    model = Group
    template_name = 'dashboard/group_details.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        ctx = super(GroupDetail, self).get_context_data(**kwargs)

        hierarchy = self.object.module
        sections = [s.id for s in hierarchy.get_root().get_descendants()]
        ctx.update(self.classify_group_users([self.object], sections))

        if ctx['completed'] > 0:
            ctx['progress_report'] = get_progress_report(
                ctx['completed_users'], hierarchy)
            ctx.pop('completed_users')

        return ctx


class StudentGroupDetail(LoggedInMixin, AdministrationOnlyMixin, TemplateView):
    '''generic class based view for
    see group details - student roster. add/remove students etc'''
    model = User
    template_name = 'dashboard/student_details.html'

    def get_context_data(self, **kwargs):
        context = super(StudentGroupDetail, self).get_context_data(**kwargs)
        group = get_object_or_404(Group, id=kwargs.get('group_id'))
        user = get_object_or_404(User, id=kwargs.get('student_id'))

        context['group'] = group
        context['student'] = user
        context['progress_report'] = get_progress_report([user], group.module)
        return context


class AggregateReportView(LoggedInMixin, AdministrationOnlyMixin,
                          JSONResponseMixin, BaseReportMixin, View):

    def post(self, request, *args, **kwargs):
        hierarchy_name = request.POST.get('module', 'main')
        hierarchy = get_object_or_404(Hierarchy, name=hierarchy_name)
        sections = [s.id for s in hierarchy.get_root().get_descendants()]

        users, groups = self.get_users_and_groups(request, hierarchy)

        if groups is None:  # reporting on unaffiliated users
            ctx = self.classify_unaffiliated_users(users, sections)
        else:
            ctx = self.classify_group_users(groups, sections)

        if ctx['completed'] > 0:
            ctx['progress_report'] = get_progress_report(
                ctx['completed_users'], hierarchy)
            ctx.pop('completed_users')

        return self.render_to_json_response(ctx)


class DownloadableReportView(LoggedInMixin, AdministrationOnlyMixin,
                             BaseReportMixin, View):

    def post(self, request):
        hierarchy_name = request.POST.get('module', 'main')
        hierarchy = get_object_or_404(Hierarchy, name=hierarchy_name)

        users, groups = self.get_users_and_groups(request, hierarchy)

        report = DetailedReport(users)

        # setup zip file for the key & value file
        response = HttpResponse(content_type='application/zip')

        disposition = 'attachment; filename=optionb.zip'
        response['Content-Disposition'] = disposition

        z = ZipFile(response, 'w')

        output = StringIO()  # temp output file
        writer = csv.writer(output)

        # report on all hierarchies
        hierarchies = Hierarchy.objects.filter(name='main')

        # Key file
        for row in report.metadata(hierarchies):
            writer.writerow(row)

        z.writestr("optionb_key.csv", output.getvalue())

        # Results file
        output.truncate(0)
        output.seek(0)

        writer = csv.writer(output)

        for row in report.values(hierarchies):
            writer.writerow(row)

        z.writestr("optionb_values.csv", output.getvalue())

        return response
