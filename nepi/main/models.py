from django.db import models
from django.db.models import signals
from django.contrib.auth.models import User
from django.db.models.signals import post_save


'''Add change delete are by default for each django model.
   Need to add permissions for visibility.'''


class UserProfile(models.Model):
    ICAP = 'IC'
    TEACHER = 'TE'
    STUDENT = 'ST'

    PROFILE_CHOICES = (
        (ICAP, 'ICAP'),
        (TEACHER, 'Teacher'),
        (STUDENT, 'Student'),
    )
    user = models.ForeignKey(User, related_name="application_user")
    profile_type = models.CharField(max_length=2, choices=PROFILE_CHOICES)

    def __unicode__(self):
        return self.user.username + " " + self.profile_type


class ICAPStaff(models.Model):
    '''How do we differentiate between ICAP admins
    (those who add modules/content) and those who
    simply edit schools etc.'''
    profile = models.ForeignKey(UserProfile)
    name = models.CharField(max_length=200)
    #region = models.CharField(max_length=200)

    def __unicode__(self):
        return self.user.username + " " + self.user.region


class Region(models.Model):
    country = models.CharField(max_length=100)
    name = models.CharField(max_length=200)


class Country(models.Model):
    ALGERIA = 'DZ'
    ANGOLA = 'AO'
    BENIN = 'BJ'
    BOTSWANA = 'BW'
    BURINKAFASO = 'BF'
    BURUNDI = 'BI'
    CAMEROON = 'CM'
    CAPEVERDE = 'CV'
    CENTRALAFRICANREPUBLIC = 'CF'
    CHAD = 'TD'
    COMORORS = 'KM'
    COTEDIVOIR = 'CI'
    DEMOCRATICREPUBLICOFCONGO = 'CD'
    DJIBOUTI = 'DJ'
    EGPYT = 'EG'
    EQUITORIALGUINEA = 'GQ'
    ERITEA = 'ER'
    ETHIOPIA = 'ET'
    GABON = 'GA'
    # http://en.wikipedia.org/wiki/List_of_sovereign_states_and_dependent_territories_in_Africa
    # http://sustainablesources.com/resources/country-abbreviations/
    # http://www.paladinsoftware.com/Generic/countries.htm

    COUNTRY_CHOICES = (

        (ALGERIA, 'Algeria'),
        (ANGOLA, 'Angola'),
        (BENIN, 'Benin'),
        (BOTSWANA, 'Botswana'),
        (BURINKAFASO, 'Burinka Faso'),
        (BURUNDI, 'Burundi'),
        (CAMEROON, 'Cameroon'),
        (CAPEVERDE, 'Cape Verde'),
    )


class School(models.Model):
    class Meta:
        permissions = (
            ("view_school", ""),
        )
    '''Some of the countries have fairly long names,
    assuming the schools may also have long names.'''
    country = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    region = models.ForeignKey(Region)
    #address?

    def __unicode__(self):
        return self.user.name + " " + self.user.country


class Teacher(models.Model):
    '''Assuming each school has many teachers but each
    teacher works at only one school.'''
    class Meta:
        permissions = (
            ("view_teacher", ""),
        )
    user = models.ForeignKey(User, related_name="teacher")
    school = models.ForeignKey(School)
    name = models.CharField(max_length=200)
    profile = models.ForeignKey(UserProfile)

    def __unicode__(self):
        return self.user.name + " " + self.user.school


class Course(models.Model):
    '''Need to store learning modules.'''
    class Meta:
        permissions = (
            ("view_course", "only the teacher of course and ICAP should see course"),
        )
    #Should limit the choices
    semester = models.CharField(max_length=200)
    content = models.CharField(max_length=200)
    teacher = models.ForeignKey(Teacher)


class Student(models.Model):
    class Meta:
        permissions = (
            ("view_students", "students should only be visible by their teacher and ICAP staff."),
        )
    '''Only designated people of the school may add teachers.'''
    school = models.ForeignKey(School)
    course = models.ManyToManyField(Course)
    #country choices should be limited
    country = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    profile = models.ForeignKey(UserProfile)
    verified = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.name + " " + self.user.country
