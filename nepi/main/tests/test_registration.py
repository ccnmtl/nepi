'''Creating test just for registration since it is prone to changing'''
from django.test import TestCase, RequestFactory
from nepi.main.models import Country, School
from nepi.main.models import PendingTeachers
from nepi.main.views import RegistrationView
from django.test.client import Client
from factories import GroupFactory
from django.core.exceptions import ValidationError


class TestRegistrationAndLogin(TestCase):
    def setUp(self):
        self.c = Client()
        self.factory = RequestFactory()
        self.country = Country(name='LS')
        self.country.save()
        self.school = School(country=self.country, name='School 1')
        self.school.save()
        self.group = GroupFactory()

    def test_student_cbv_reg(self):
        request = self.factory.post(
            "/register/",
            {"first_name": "regstudent", "last_name": "regstudent",
             "username": "regstudent", "email": "test_email@email.com",
             "password1": "regstudent", "password2": "regstudent",
             "country": "LS", "profile_type": False,
             "captcha": True})
        response = RegistrationView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        # should redirect, request factory can't follow linkes like client

    def test_student_registration_and_login(self):
        '''when students are registered they should not be added to pending'''
        response = self.c.post(
            '/register/',
            {"first_name": "regstudent", "last_name": "regstudent",
             "username": "regstudent", "email": "test_email@email.com",
             "password1": "regstudent", "password2": "regstudent",
             "country": "LS", "profile_type": False,
             "captcha": True}, follow=True)
        self.assertEquals(response.status_code, 200)
        self.pending = PendingTeachers.objects.all()
        self.assertFalse(self.pending.count())
        # apparently [] stands for root or '/'
        self.assertEquals(response.redirect_chain, [])
        self.assertTemplateUsed('dashboard/student_dashboard.html')

    def test_teacher_registration_and_login_request_factory(self):
        '''when teachers register they should
        be added to the pending teachers table
        - but dont know how to test for that.'''
        request = RequestFactory().get('/register/')
        view = RegistrationView.as_view()
        response = view(request, data={"first_name": "reg_teacher",
                                       "last_name": "reg_teacher",
                                       "username": "reg_teacher",
                                       "email": "test_email@email.com",
                                       "password1": "reg_teacher",
                                       "password2": "reg_teacher",
                                       "country": "LS",
                                       "profile_type": True,
                                       "captcha": True})
        self.assertEquals(response.status_code, 200)

    def test_teacher_registration_client(self):
        '''when teachers register they should
        be added to the pending teachers table
        - but dont know how to test for that.'''
        request = self.c.post(
            '/register/',
            {"first_name": "reg_teacher", "last_name": "reg_teacher",
             "username": "reg_teacher", "email": "test_email@email.com",
             "password1": "reg_teacher", "password2": "reg_teacher",
             "country": "LS", "profile_type": True,
             "captcha": True}, follow=True)
        self.assertEquals(request.status_code, 200)

    def test_teacher_registration_no_email(self):
        '''when teachers register but do not provide email
        an error should be thrown.'''
        request = self.c.post(
            '/register/',
            {"first_name": "reg_teacher", "last_name": "reg_teacher",
             "username": "reg_teacher", "email": "",
             "password1": "reg_teacher", "password2": "reg_teacher",
             "country": "LS", "profile_type": True,
             "captcha": True}, follow=True)
        self.asserttRaises(ValidationError, request)
