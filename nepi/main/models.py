from __future__ import unicode_literals

import base64
from datetime import timedelta
import datetime
import hashlib
import hmac

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.core.cache import cache
from django.db import models
from django.db.models.aggregates import Min, Max
from django.db.models.query_utils import Q
from django.utils.encoding import (
    smart_str, smart_bytes
)
from django.utils.translation import get_language_info
from pagetree.models import Hierarchy, UserPageVisit, PageBlock
from pagetree.reports import PagetreeReport, StandaloneReportColumn


PROFILE_CHOICES = (
    ('ST', 'Student'),
    ('TE', 'Teacher'),
    ('IN', 'Institution'),
    ('CA', 'Country Administrator'),
    ('IC', 'ICAP')
)


class LearningModule(object):
    ''' Placeholder for an object that holds the language-based hierarchies
        for a single learning experience, e.g. optionb-en, optionb-fr...
    '''

    @classmethod
    def get_hierarchy_for_language(cls, module, language):
        hierarchy_name = '%s-%s' % (module, language)
        return Hierarchy.objects.get(name=hierarchy_name)

    @classmethod
    def get_hierarchies_for_module(cls, module_name):
        h = Hierarchy.objects.filter(name__startswith=module_name)
        return h.exclude(name__contains='bk')  # backup on production

    @classmethod
    def get_module_name(cls, hierarchy):
        return hierarchy.name.split('-')[0]

    @classmethod
    def get_module_language(cls, hierarchy):
        code = hierarchy.name.split('-')[1]
        li = get_language_info(code)
        return li['name']


class HierarchyCache(object):

    @classmethod
    def get_descendants(cls, section):
        key = 'hierarchy_%s_section_%s' % (section.hierarchy.id, section.id)
        descendants = cache.get(key)
        if descendants is None:
            descendants = section.get_descendants()
            cache.set(key, descendants)
        return descendants

    @classmethod
    def get_descendant_ids(cls, section):
        key = 'hierarchy_%s_sectionids_%s' % (section.hierarchy.id, section.id)
        ids = cache.get(key)
        if ids is None:
            descendants = HierarchyCache.get_descendants(section)
            ids = [s.id for s in descendants]
            cache.set(key, ids)
        return ids


class Country(models.Model):
    '''Users can select counties from drop down menu,
    countries are stored by their official 2 letter codes.'''
    name = models.CharField(max_length=2, unique=True)
    display_name = models.TextField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.display_name

    @classmethod
    def choices(cls):
        return [(c.name, c.display_name)
                for c in Country.objects.all().order_by('display_name')]


class School(models.Model):
    '''Some of the countries have fairly long names,
    assuming the schools may also have long names.'''
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024)

    class Meta:
        ordering = ['name']
        unique_together = ['name', 'country']

    def __str__(self):
        return '%s - %s' % (self.country.display_name, self.name)


class Group(models.Model):
    '''Allow association of group with module.'''
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    name = models.CharField(max_length=50)
    creator = models.ForeignKey(
        User, related_name="created_by", on_delete=models.CASCADE)
    module = models.ForeignKey(
        Hierarchy, null=True, default=None, blank=True,
        on_delete=models.CASCADE)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def created_by(self):
        return self.creator

    def format_time(self, dt):
        return dt.strftime("%m/%d/%Y")

    def formatted_start_date(self):
        return self.format_time(self.start_date)

    def formatted_end_date(self):
        return self.format_time(self.end_date)

    def is_active(self):
        today = datetime.date.today()
        diff = today - self.end_date
        return diff.days < 365

    def description(self):
        return "%s %s" % (self.name, self.school)

    def students(self):
        students = self.userprofile_set.filter(profile_type='ST')
        return students.order_by('user__last_name', 'user__first_name')

    def module_name(self):
        return LearningModule.get_module_name(self.module)


class UserProfile(models.Model):
    '''UserProfile adds extra information to a user,
    and associates the user with a group, school,
    and country.'''
    user = models.OneToOneField(
        User, related_name="profile", on_delete=models.CASCADE)
    profile_type = models.CharField(max_length=2, choices=PROFILE_CHOICES)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    icap_affil = models.BooleanField(default=False)
    school = models.ForeignKey(
        School, null=True, default=None, blank=True, on_delete=models.CASCADE)
    group = models.ManyToManyField(
        Group, default=None, blank=True)
    language = models.CharField(max_length=255,
                                choices=settings.LANGUAGES,
                                default=settings.DEFAULT_LANGUAGE)

    def __str__(self):
        return self.user.username

    class Meta:
        ordering = ["user"]

    def last_location(self, hierarchy):
        visits = UserPageVisit.objects.filter(user=self.user,
                                              section__hierarchy=hierarchy)

        if visits.count() < 1:
            return hierarchy.get_root()
        else:
            visits = visits.order_by('-last_visit')
            return visits[0].section

    @classmethod
    def format_timedelta(cls, delta):
        hours, remainder = divmod(delta.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        return '%02d:%02d:%02d' % (hours, minutes, seconds)

    def time_spent(self, hierarchy):
        visits = UserPageVisit.objects.filter(
            user=self.user, status='complete', section__hierarchy=hierarchy)

        if visits.count() < 1:
            return '00:00:00'

        five_minutes = timedelta(minutes=5)
        time_spent = timedelta(0)

        prev = None
        for page in visits.order_by('first_visit'):
            if prev:
                interval = (page.first_visit - prev)
                # record 5 minutes for any interval longer than 5 minutes
                time_spent += min(interval, five_minutes)
            prev = page.first_visit

        return self.format_timedelta(time_spent)

    def time_elapsed(self, hierarchy):
        visits = UserPageVisit.objects.filter(
            user=self.user, status='complete', section__hierarchy=hierarchy)

        if visits.count() < 1:
            return '00:00:00'

        results = visits.aggregate(Min('first_visit'), Max('last_visit'))
        elapsed = results['last_visit__max'] - results['first_visit__min']
        return self.format_timedelta(elapsed)

    def percent_complete(self, parent_section):
        section_ids = HierarchyCache.get_descendant_ids(parent_section)
        count = len(section_ids)
        if count > 0:
            visits = UserPageVisit.objects.filter(user=self.user,
                                                  status='complete',
                                                  section__in=section_ids)
            return len(visits) / float(count) * 100
        else:
            return 100  # this section has no children.

    def sessions_completed(self, hierarchy):
        complete = 0

        for session in hierarchy.get_root().get_children():
            if self.percent_complete(session) == 100:
                complete += 1
        return complete

    def completion_date(self, hierarchy):
        sections = HierarchyCache.get_descendants(hierarchy.get_root())
        last_section = sections[len(sections) - 1]

        visits = UserPageVisit.objects.filter(user=self.user,
                                              status='complete',
                                              section=last_section)

        if visits.count() < 1:
            return None
        else:
            return visits[0].first_visit

    def display_name(self):
        return self.user.username

    def is_student(self):
        return self.profile_type == 'ST'

    def is_teacher(self):
        return self.profile_type == 'TE'

    def is_institution_administrator(self):
        return self.profile_type == 'IN'

    def is_country_administrator(self):
        return self.profile_type == 'CA'

    def is_icap(self):
        return self.profile_type == 'IC'

    def role(self):
        if self.is_student():
            return "student"
        elif self.is_teacher():
            return "faculty"
        elif self.is_institution_administrator():
            return "institution"
        elif self.is_country_administrator():
            return "country"
        elif self.is_icap():
            return "icap"

    def joined_groups(self):
        '''Groups this user has joined'''
        return self.group.exclude(archived=True)

    def is_pending_teacher(self):
        return PendingTeachers.objects.filter(user_profile=self).count() > 0

    def get_managed_groups(self):
        if self.is_student():
            return Group.objects.none()

        if self.is_teacher():
            groups = Group.objects.filter(creator=self.user)
            groups = groups.order_by('name')
        elif self.is_institution_administrator():
            groups = Group.objects.filter(
                Q(creator=self.user) | Q(school=self.school))
        elif self.is_country_administrator():
            groups = Group.objects.filter(
                Q(creator=self.user) | Q(school__country=self.country))
        elif self.is_icap():
            groups = Group.objects.all()

        groups = groups.exclude(archived=True)
        return groups.order_by(
            'school__country__display_name', 'school__name', 'name')

    def get_groups_by_hierarchy(self, hierarchy_name):
        groups = self.joined_groups().filter(module__name=hierarchy_name)
        return [grp.description() for grp in groups]

    def get_preferred_language(self):
        li = get_language_info(self.language)
        return li['name']


class PendingTeachers(models.Model):
    user_profile = models.ForeignKey(UserProfile,
                                     related_name="pending_teachers",
                                     on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)

    def __str__(self):
        return "%s - %s" % (self.user_profile, self.school)


class AggregateQuizScore(models.Model):
    pageblocks = GenericRelation(
        PageBlock, related_query_name="aggregate_quiz_score")
    quiz_class = models.TextField()
    display_name = 'Aggregate Quiz Score'
    template_file = "main/aggregate_quiz_score.html"

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __str__(self):
        return "%s -- %s" % (smart_str(self.pageblock()), self.quiz_category)

    @classmethod
    def add_form(self):
        return AggregateQuizScoreForm()

    def edit_form(self):
        return AggregateQuizScoreForm(instance=self)

    @classmethod
    def create(self, request):
        form = AggregateQuizScoreForm(request.POST)
        return form.save()

    def edit(self, vals, files):
        form = AggregateQuizScoreForm(data=vals, files=files, instance=self)
        if form.is_valid():
            form.save()

    def needs_submit(self):
        return False

    def unlocked(self, user):
        return True


class AggregateQuizScoreForm(forms.ModelForm):
    class Meta:
        model = AggregateQuizScore
        exclude = []


def random_user(username):
    username = smart_str(username)
    digest = hmac.new(smart_bytes(settings.PARTICIPANT_SECRET),
                      msg=smart_bytes(username),
                      digestmod=hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


class DetailedReport(PagetreeReport):

    def __init__(self, hierarchy, users):
        self.all_users = users
        self.hierarchy = hierarchy
        self.root = hierarchy.get_root()
        super(DetailedReport, self).__init__()

    def users(self):
        return self.all_users

    def standalone_columns(self):
        from nepi.main.templatetags.progressreport import average_quiz_score
        from nepi.main.templatetags.progressreport import completed

        return [
            StandaloneReportColumn(
                'participant_id', 'profile', 'string',
                'Randomized Participant Id',
                lambda x: random_user(x.username)),
            StandaloneReportColumn(
                'country', 'profile', 'string',
                'affiliated country',
                lambda x: smart_str(x.profile.country.display_name)),
            StandaloneReportColumn(
                'group', 'profile', 'list',
                'Groups',
                lambda x: ','.join(
                    x.profile.get_groups_by_hierarchy(self.hierarchy))),
            StandaloneReportColumn(
                'completed', 'profile', 'boolean',
                'pages visits + pre + post tests',
                lambda x: completed(x, self.hierarchy)),
            StandaloneReportColumn(
                'percent_complete', 'profile', 'percent',
                '% of hierarchy completed',
                lambda x: x.profile.percent_complete(self.root)),
            StandaloneReportColumn(
                'total_time_elapsed', 'profile', 'hours:minutes:seconds',
                'total time period over which the module was accessed',
                lambda x: x.profile.time_elapsed(self.hierarchy)),
            StandaloneReportColumn(
                'actual_time_spent', 'profile', 'hours:minutes:seconds',
                'actual time spent completing the module',
                lambda x: x.profile.time_spent(self.hierarchy)),
            StandaloneReportColumn(
                'completion_date', 'profile', 'date/time',
                'the date the user completed the module',
                lambda x: x.profile.completion_date(self.hierarchy)),
            StandaloneReportColumn(
                'pre-test score', 'profile', 'percent',
                'Pre-test Score',
                lambda x: average_quiz_score([x], self.hierarchy, 'pretest')),
            StandaloneReportColumn(
                'post-test score', 'profile', 'percent',
                'Post-test Score',
                lambda x: average_quiz_score([x], self.hierarchy, 'posttest')),
            ]
