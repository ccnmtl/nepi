from choices import COUNTRY_CHOICES, PROFILE_CHOICES
from django import forms
import base64
import hashlib
import hmac
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from pagetree.models import Hierarchy, UserPageVisit, PageBlock
from pagetree.reports import PagetreeReport, StandaloneReportColumn
from quizblock.models import Quiz
import datetime


class Country(models.Model):
    '''Users can select counties from drop down menu,
    countries are stored by their official 2 letter codes.'''
    name = models.CharField(max_length=2, choices=COUNTRY_CHOICES, unique=True)
    display_name = models.TextField()

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.display_name


class School(models.Model):
    '''Some of the countries have fairly long names,
    assuming the schools may also have long names.'''
    country = models.ForeignKey(Country)
    name = models.CharField(max_length=1024)

    class Meta:
        ordering = ['name']
        unique_together = ['name', 'country']

    def __unicode__(self):
        return '%s - %s' % (self.country.display_name, self.name)


class Group(models.Model):
    '''Allow association of group with module.'''
    school = models.ForeignKey(School)
    start_date = models.DateField()
    end_date = models.DateField()
    name = models.CharField(max_length=50)
    creator = models.ForeignKey(User, related_name="created_by")
    module = models.ForeignKey(Hierarchy, null=True, default=None, blank=True)
    archived = models.BooleanField(default=False)

    def __unicode__(self):
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


class UserProfile(models.Model):
    '''UserProfile adds exta information to a user,
    and associates the user with a group, school,
    and counrty.'''
    user = models.OneToOneField(User, related_name="profile")
    profile_type = models.CharField(max_length=2, choices=PROFILE_CHOICES)
    country = models.ForeignKey(Country)
    icap_affil = models.BooleanField(default=False)
    school = models.ForeignKey(School, null=True, default=None, blank=True)
    group = models.ManyToManyField(
        Group, null=True, default=None, blank=True)

    def __unicode__(self):
        return self.user.username

    class Meta:
        ordering = ["user"]

    def last_location(self, hierarchy):
        visits = UserPageVisit.objects.filter(user=self.user)

        if visits.count() < 1:
            return hierarchy.get_root()
        else:
            visits = visits.order_by('-last_visit')
            return visits[0].section

    def percent_complete(self, parent_section):
        sections = parent_section.get_descendants()
        if len(sections) > 0:
            ids = [s.id for s in sections]
            visits = UserPageVisit.objects.filter(user=self.user,
                                                  section__in=ids)
            return len(visits) / float(len(sections)) * 100
        else:
            return 100  # this section has no children.

    def sessions_completed(self, hierarchy):
        complete = 0

        for session in hierarchy.get_root().get_children():
            if self.percent_complete(session) == 100:
                complete += 1
        return complete

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

    def get_groups_by_hierarchy(self, hierarchy_name):
        groups = self.joined_groups()
        group = groups.filter(module__name=hierarchy_name)
        grp = [str(group.name), str(group.school), str(group.school.country)]
        return grp


class PendingTeachers(models.Model):
    user_profile = models.ForeignKey(UserProfile,
                                     related_name="pending_teachers")
    school = models.ForeignKey(School)

    def __unicode__(self):
        return "%s - %s" % (self.user_profile, self.school)


class AggregateQuizScore(models.Model):
    pageblocks = generic.GenericRelation(
        PageBlock, related_name="aggregate_quiz_score")
    quiz_class = models.TextField()
    display_name = 'Aggregate Quiz Score'
    template_file = "main/aggregate_quiz_score.html"

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __unicode__(self):
        return "%s -- %s" % (unicode(self.pageblock()), self.quiz_category)

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

    def quizzes(self):
        ctype = ContentType.objects.get_for_model(Quiz)
        blocks = PageBlock.objects.filter(content_type__pk=ctype.pk,
                                          css_extra__contains=self.quiz_class)
        ids = blocks.values_list('object_id', flat=True)
        return Quiz.objects.filter(id__in=ids)


class AggregateQuizScoreForm(forms.ModelForm):
    class Meta:
        model = AggregateQuizScore


def random_user(username):
    digest = hmac.new(settings.PARTICIPANT_SECRET,
                      msg=username, digestmod=hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


class OptionBReport(PagetreeReport):

    def __init__(self, groups):
        self.groups = groups

    def users(self):
        group_ids = self.groups.values_list('id', flat=True)
        users = User.objects.filter(profile__group__id__in=group_ids,
                                    profile__profile_type='ST')
        return users.order_by('id')

    def standalone_columns(self):
        return [
            StandaloneReportColumn(
                "participant_id", 'profile', 'string',
                'Randomized Participant Id',
                lambda x: random_user(x.username)),
            StandaloneReportColumn(
                "optionb_percent_complete", 'profile', 'percent',
                '% of hierarchy completed',
                lambda x: x.profile.percent_complete_hierarchy('main')),
            StandaloneReportColumn(
                "group", 'profile', 'list',
                'Option B+ Groups',
                lambda x: ",".join(x.profile.get_groups_by_hierarchy('main'))),
            ]
