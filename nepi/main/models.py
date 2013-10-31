from django.db import models
from django.db.models import signals
from django.contrib.auth.models import User
from django.db.models.signals import post_save


'''Add change delete are by default for each django model. Need to add permissions for visibility.'''

class UserProfile(models.Model):
    ICAPADMIN = 'IA'
    ICAPSTAFF = 'IS'
    TEACHER = 'TE'
    SCHOOLSTAFF = 'SS'
    STUDENT = 'ST'

    PROFILE_CHOICES = (
        (ICAPADMIN, 'ICAPAdmin'),
        (ICAPSTAFF, 'ICAPStaff'),
        (TEACHER, 'Teacher'),
        (SCHOOLSTAFF, 'SchoolStaff'),
        (STUDENT, 'Student'),
    )
    user = models.ForeignKey(User, related_name="application_user")
    profile_type = models.CharField(max_length=2,choices=PROFILE_CHOICES)

    def __unicode__(self):
        return self.user.username



class ICAPAdmin(models.Model):
    '''How do we differentiate between ICAP admins
    (those who add modules/content) and those who 
    simply edit schools etc.'''
    profile = models.ForeignKey(UserProfile)
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.user.username + " " + self.user.region


class ICAPStaff(models.Model):
    '''How do we differentiate between ICAP admins
    (those who add modules/content) and those who 
    simply edit schools etc.'''
    profile = models.ForeignKey(UserProfile)
    region = models.CharField(max_length=100)
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.user.username + " " + self.user.region


class School(models.Model):
    class Meta:
        permissions = (
            ("view_school", ""),
            #("view_teachers", ""),
            #("view_courses", ""),
        )
    '''Some of the countries have fairly long names,
    assuming the schools may also have long names.'''
    country = models.CharField(max_length=100)
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.user.name + " " + self.user.country


class Teacher(models.Model):
    '''Assuming each school has many teachers but each
    teacher works at only one school.'''
    user = models.ForeignKey(User, related_name="teacher")
    school = models.ForeignKey(School)
    name = models.CharField(max_length=200)
    profile = models.ForeignKey(UserProfile)

    def __unicode__(self):
        return self.user.name + " " + self.user.school


class SchoolStaff(models.Model):
    '''Only designated people of the school may add teachers.'''
    country = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    profile = models.ForeignKey(UserProfile)

    def __unicode__(self):
        return self.user.name + " " + self.user.country


class Course(models.Model):
    '''Need to store learning modules.'''
    class Meta:
        permissions = (
            ("view_course", "determine if the course can be viewed by a user"),
        )
    content = models.CharField(max_length=200)
    teacher = models.ForeignKey(Teacher)
    #teacher = models.ManyToManyField(Teacher)
    #are we dealing ONLY with individual courses? or many?

class Student(models.Model):
    '''Only designated people of the school may add teachers.'''
    school = models.ForeignKey(School)
    course = models.ManyToManyField(Course)
    country = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    profile = models.ForeignKey(UserProfile)
    verified = models.BooleanField(default=False)

    def __unicode__(self):
        return self.user.name + " " + self.user.country






