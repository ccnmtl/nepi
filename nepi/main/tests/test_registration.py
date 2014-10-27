from django.contrib.auth.models import User
from django.test.client import Client
from django.test.testcases import TestCase
from nepi.main.models import PendingTeachers
from nepi.main.tests.factories import UserFactory, SchoolFactory, \
    CountryFactory
from nepi.main.views import RegistrationView


class TestRegistrationView(TestCase):
    def setUp(self):
        self.view = RegistrationView()
        self.existing_user = UserFactory()
        self.client = Client()

        self.country = CountryFactory(name='LS')
        self.school = SchoolFactory(country=self.country)

    def test_student_registration_view_duplicate(self):
        response = self.client.post(
            '/register/',
            {"first_name": "regstudent", "last_name": "regstudent",
             "username": self.existing_user.username,
             "email": "test_email@email.com",
             "password1": "test", "password2": "test",
             "country": self.country.name, "nepi_affiliated": False,
             "captcha_0": 'dummy_value', "captcha_1": 'PASSED'}, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('username' in response.context_data['form']._errors)

    def test_student_registration_valid_username(self):
        data = {
            "first_name": "regstudent", "last_name": "regstudent",
            "email": "test_email@email.com",
            "password1": "test", "password2": "test",
            "country": self.country.name, "nepi_affiliated": False,
            "captcha_0": 'dummy_value', "captcha_1": 'PASSED'}

        data['username'] = ' spaces '
        response = self.client.post('/register/', data, follow=True)
        self.assertTrue('username' in response.context_data['form']._errors)

        data['username'] = 'sp aces'
        response = self.client.post('/register/', data, follow=True)
        self.assertTrue('username' in response.context_data['form']._errors)

        data['username'] = 'foo18@#$%^'
        response = self.client.post('/register/', data, follow=True)
        self.assertTrue('username' in response.context_data['form']._errors)

        data['username'] = 'valid1_username'
        response = self.client.post('/register/', data, follow=True)
        self.assertFalse('form' in response.context_data)

    def test_student_registration_no_internal_spaces(self):
        response = self.client.post(
            '/register/',
            {"first_name": "regstudent", "last_name": "regstudent",
             "username": "foo bar",
             "email": "test_email@email.com",
             "password1": "test", "password2": "test",
             "country": self.country.name, "nepi_affiliated": False,
             "captcha_0": 'dummy_value', "captcha_1": 'PASSED'}, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('username' in response.context_data['form']._errors)

    def test_student_registration_view(self):
        '''when students are registered they should not be added to pending'''
        response = self.client.post(
            '/register/',
            {"first_name": "regstudent", "last_name": "regstudent",
             "username": "student", "email": "test_email@email.com",
             "password1": "test", "password2": "test",
             "country": self.country.name, "nepi_affiliated": False,
             "captcha_0": 'dummy_value', "captcha_1": 'PASSED'}, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(PendingTeachers.objects.count(), 0)

        self.assertEquals(response.redirect_chain,
                          [('http://testserver/account_created/', 302)])
        self.assertTemplateUsed(response, 'flatpages/account_created.html')

        student = User.objects.get(username='student')
        self.assertFalse(student.profile.icap_affil)

        self.assertTrue(Client().login(username='student', password="test"))

    def test_teacher_registration_view(self):
        response = self.client.post(
            '/register/',
            {"first_name": "first", "last_name": "last",
             "username": "teacher", "email": "test_email@email.com",
             "password1": "test", "password2": "test", "profile_type": True,
             "country": self.country.name, "school": self.school.id,
             "nepi_affiliated": True,
             "captcha_0": 'dummy_value', "captcha_1": 'PASSED'}, follow=True)
        self.assertEquals(response.status_code, 200)

        self.assertEquals(PendingTeachers.objects.count(), 1)

        self.assertEquals(response.redirect_chain,
                          [('http://testserver/account_created/', 302)])
        self.assertTemplateUsed(response, 'flatpages/account_created.html')

        teacher = User.objects.get(username='teacher')
        self.assertTrue(teacher.profile.icap_affil)

        self.assertTrue(Client().login(username='teacher', password="test"))
