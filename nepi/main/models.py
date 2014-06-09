from django.contrib.auth.models import User
from django.db import models
from choices import COUNTRY_CHOICES, PROFILE_CHOICES
from pagetree.models import Section, Hierarchy, UserLocation, UserPageVisit


'''Add change delete are by default for each django model.
   Need to add permissions for visibility.'''


class Country(models.Model):
    '''Users can select counties from drop down menu,
    countries are stored by their official 2 letter codes.'''
    name = models.CharField(max_length=2, choices=COUNTRY_CHOICES, blank=True)

    def __unicode__(self):
        return self.name


class School(models.Model):
    '''Some of the countries have fairly long names,
    assuming the schools may also have long names.'''
    country = models.ForeignKey(Country, blank=True, default=None)
    name = models.CharField(blank=True, max_length=50)

    def __unicode__(self):
        return self.name


class Course(models.Model):
    '''Allow association of course with module.'''
    school = models.ForeignKey(School)
    # semester = models.CharField(max_length=50, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    name = models.CharField(max_length=50)
    creator = models.ForeignKey(User, related_name="created_by",
                                null=True, default=None, blank=True)
    module = models.ForeignKey(Hierarchy, null=True, default=None, blank=True)

    def __unicode__(self):
        return self.name

    def created_by(self):
        return self.creator


'''ADD VALIDATION'''


class UserProfile(models.Model):
    '''UserProfile adds exta information to a user,
    and associates the user with a course, school,
    and counrty.'''
    user = models.ForeignKey(User, related_name="application_user")
    profile_type = models.CharField(max_length=2, choices=PROFILE_CHOICES)
    country = models.ForeignKey(Country, null=True, default=None, blank=True)
    # not sure why we are saving this in user profile
    icap_affil = models.BooleanField(default=False)
    school = models.ForeignKey(School, null=True, default=None, blank=True)
    course = models.ManyToManyField(
        Course, null=True, default=None, blank=True)

    def __unicode__(self):
        return self.user.username

    class Meta:
        ordering = ["user"]

    def get_has_visited(self, section):
        return section.get_uservisit(self.user) is not None

    def set_has_visited(self, sections):
        for sect in sections:
            sect.user_pagevisit(self.user, "complete")
            sect.user_visit(self.user)

    def last_location(self, hierarchy_name=None):
        if hierarchy_name is None:
            hierarchy_name = self.role()
        hierarchy = Hierarchy.get_hierarchy(hierarchy_name)
        try:
            UserLocation.objects.get(user=self.user,
                                     hierarchy=hierarchy)
            return hierarchy.get_user_section(self.user)
        except UserLocation.DoesNotExist:
            return hierarchy.get_first_leaf(hierarchy.get_root())

    def percent_complete(self):
        hierarchy = Hierarchy.get_hierarchy(self.role())
        visits = UserPageVisit.objects.filter(section__hierarchy=hierarchy)
        sections = Section.objects.filter(hierarchy=hierarchy)
        if len(sections) > 0:
            return int(len(visits) / float(len(sections)) * 100)
        else:
            return 0

    def display_name(self):
        return self.user.username

    def is_student(self):
        return self.profile_type == 'ST'

    def is_teacher(self):
        return self.profile_type == 'TE'

    def is_icap(self):
        return self.profile_type == 'IC'

    def role(self):
        if self.is_student():
            return "student"
        elif self.is_teacher():
            return "teacher"
        elif self.is_icap():
            return "icap"


class PendingTeachers(models.Model):
    user_profile = models.ForeignKey(UserProfile,
                                     related_name="pending_teachers")
    school = models.ForeignKey(School, null=True, default=None)
