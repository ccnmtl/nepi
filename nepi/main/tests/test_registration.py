'''Creating test just for registration since it is prone to changing'''
from django.test import TestCase
from django.contrib.auth.models import User
from nepi.main.models import UserProfile, Country, School
from nepi.main.models import Course, PendingTeachers
from nepi.main.views import register
from datetime import datetime
from django.test import TestCase, RequestFactory


class TestRegistration(TestCase):
    def setUp(self):
        self.country = Country(name='LS', region='Region 1')
        self.school = School(country=self.country1, name='School 1')
        self.country.save()
        self.school.save()
        self.course = Course(school=self.school,
                             semester="Fall 2018", name="Course",
                             start_date=datetime.now(),
                             end_date=datetime.now())



        self.student = User(first_name="student", last_name="student",
                            username="student", email="student@email.com",
                            password="student")
        self.student.save()
        self.teacher = User(first_name="teacher", last_name="teacher",
                            username="teacher", email="teacher@email.com",
                            password="teacher")
        self.teacher.save()


    def test_student_registration_and_login(self):
        request = self.factory.post(
            '/register/',
            {"first_name": "firstname", "last_name": "lastname",
             "username": "username", "email": "test_email@email.com",
             "password1": "password", "password2": "password",
             "country" : "LS", "profile_type":"ST"})
        response = create_account(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(PendingTeachers.objects.count(), 0)


    def test_teacher_registration_and_login(self):
        request = self.factory.post(
            '/register/',
            {"first_name": "firstname", "last_name": "lastname",
             "username": "username", "email": "test_email@email.com",
             "password1": "password", "password2": "password",
             "country" : "LS", "profile_type":"TE"})
        response = create_account(request)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PendingTeachers.objects.count() > 0)
        self.assertTrue(PendingTeachers.objects.filter(fist_name="firstname"))
