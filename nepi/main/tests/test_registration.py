'''Creating test just for registration since it is prone to changing'''
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from nepi.main.models import Country, School
from nepi.main.models import Course, PendingTeachers
from nepi.main.views import RegistrationView
from datetime import datetime
from django.test.client import Client

class TestRegistration(TestCase):
    def setUp(self):
        self.c = Client()
        self.factory = RequestFactory()
        self.country = Country(name='LS', region='Region 1')
        self.country.save()
        self.school = School(country=self.country, name='School 1')
        self.school.save()
        self.course = Course(school=self.school,
                             semester="Fall 2018", name="Course",
                             start_date=datetime.now(),
                             end_date=datetime.now())
        self.course.save()
#         self.student = User(first_name="student", last_name="student",
#                             username="student", email="student@email.com",
#                             password="student")
#         self.student.save()
#         self.teacher = User(first_name="teacher", last_name="teacher",
#                             username="teacher", email="teacher@email.com",
#                             password="teacher")
#         self.teacher.save()

    def test_student_registration_and_login(self):
        '''when students are registered they should not be added to pending'''
        #response = self.factory.post(   why did I have factory post here?
        response = self.c.post(
            '/register/',
            {"first_name": "regstudent", "last_name": "regstudent",
             "username": "regstudent", "email": "test_email@email.com",
             "password1": "regstudent", "password2": "regstudent",
             "country": "LS", "profile_type": False, "captcha": True}, follow=True)
        self.assertEquals(response.status_code, 200)
        self.pending = PendingTeachers.objects.all()
        self.assertFalse(self.pending.count())
        #self.assertEquals(response.redirect_chain,
        #                  ('http://testserver/thank_you_reg/',
        #                   302))
        #self.assertTemplateUsed('flatpages/help.html')
        #self.assertTrue()/thank_you_reg/
        #RegistrationView.as_view()(request)

    def test_teacher_registration_and_login(self):
        '''when teachers register they should
        be added to the pending teachers table'''
        response = self.c.post(
            '/register/',
            {"first_name": "reg_teacher", "last_name": "reg_teacher",
             "username": "reg_teacher", "email": "test_email@email.com",
             "password1": "reg_teacher", "password2": "reg_teacher",
             "country": "LS", "profile_type": True, "captcha": True})
        self.assertEquals(response.status_code, 200)
        self.pending = PendingTeachers.objects.all()
        self.assertTrue(self.pending.count())
        # I don't remember why I put this here
        # RegistrationView.as_view()(request)
        # new_teacher = User.objects.get(first_name="firstname")
        # self.assertTrue(new_teacher)
