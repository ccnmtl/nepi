from django.test import TestCase
from django.contrib.auth.models import User
#from pagetree.models import Hierarchy, Section
from nepi.main.models import UserProfile, Country, School
from nepi.main.models import LearningModule, Course
from nepi.main.models import PendingRegister
from django import forms
from datetime import datetime

class TestUserProfile(TestCase):
    def setUp(self):
        self.student = User(first_name="student",last_name="student",username="student",email="student@email.com",password="student")
        self.student.save()
        self.teacher = User(first_name="teacher",last_name="teacher",username="teacher",email="teacher@email.com",password="teacher")
        self.teacher.save()
        self.icap = User(first_name="icapp",last_name="icapp",username="icapp",email="icapp@email.com",password="icapp")
        self.icap.save()
        self.country1 = Country(country='LS', region='Region 1')
        self.country1.save()
        self.country2 = Country(country='GM', region='Region 1')
        self.country1.save()
        self.country3 = Country(country='TG', region='Region 1')
        self.country1.save()
        self.school = School(country=self.country1,name='School 1')
        self.school.save()
        self.learningmodule = LearningModule(name="Learning Module 1", description="first learning module")
        self.learningmodule.save()
        self.course = Course(school=self.school, module=self.learningmodule, semester="Fall 2018", name="Course", start_date=datetime.now(), end_date=datetime.now())
        self.course.save()
        self.student_profile = UserProfile(user=self.student, profile_type='ST', country=self.country1, school=self.school)
        #self.student_profile.course=self.course
        self.student_profile.save()
        #self.student_profile.course=self.course
        #self.student_profile.save()
        self.teacher_profile = UserProfile(user=self.teacher, profile_type='TE', country=self.country1, school=self.school)
        self.teacher_profile.save()
        self.icap_profile = UserProfile(user=self.icap, profile_type='IC', country=self.country1, school=self.school)
        self.icap_profile.save()

    def test_user_profile_unis(self):
        self.assertEquals(unicode(self.student), "student")
        self.assertEquals(unicode(self.teacher), "teacher")
        self.assertEquals(unicode(self.icap), "icapp")



