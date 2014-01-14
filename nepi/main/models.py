from django.db import models
from django.contrib.auth.models import User
from nepi.main.choices import COUNTRY_CHOICES, PROFILE_CHOICES
from pagetree.models import Section, Hierarchy


'''Add change delete are by default for each django model.
   Need to add permissions for visibility.'''


# from tobacco
class UserVisit(models.Model):
    section = models.ForeignKey(Section)
    count = models.IntegerField(default=1)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s %d %s" % (self.section, self.count, self.created)


class Country(models.Model):
    name = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    region = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class School(models.Model):
    '''Some of the countries have fairly long names,
    assuming the schools may also have long names.'''
    country = models.ForeignKey(Country, blank=True, default=None)
    name = models.CharField(null=True, max_length=50)

    def __unicode__(self):
        return self.name


class Course(models.Model):
    '''Allow association of course with module.'''
    school = models.ForeignKey(School, blank=True, default=None)
    semester = models.CharField(max_length=50, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    name = models.CharField(max_length=50, blank=True)

    def __unicode__(self):
        return self.name


class UserProfile(models.Model):
    user = models.ForeignKey(User, related_name="application_user")
    visits = models.ManyToManyField(UserVisit, null=True, blank=True)
    profile_type = models.CharField(max_length=2, choices=PROFILE_CHOICES)
    country = models.ForeignKey(Country, null=True, blank=True)
    school = models.ForeignKey(School, null=True, default=None)
    course = models.ManyToManyField(Course, null=True, blank=True)

    def __unicode__(self):
        return self.user.username

    class Meta:
        ordering = ["user"]

# All of the following taken from Tobacco
    def get_has_visited(self, section):
        return len(self.visits.filter(section=section)) > 0

    def set_has_visited(self, sections):
        for sect in sections:
            visits = self.visits.filter(section=sect)
            if len(visits) > 0:
                visits[0].count = visits[0].count + 1
                visits[0].save()
            else:
                visit = UserVisit(section=sect)
                visit.save()
                self.visits.add(visit)

    def last_location(self):
        visits = self.visits.order_by('-modified')
        if len(visits) > 0:
            return visits[0].section
        else:
            hierarchy = Hierarchy.get_hierarchy(self.role())
            return hierarchy.get_first_leaf(hierarchy.get_root())

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

    def percent_complete(self):
        hierarchy = Hierarchy.get_hierarchy(self.role())
        profile = UserProfile.objects.get(user=self.user)
        sections = Section.objects.filter(hierarchy=hierarchy)
        return int(len(profile.visits.all()) / float(len(sections)) * 100)
