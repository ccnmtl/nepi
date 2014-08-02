from django.contrib.auth.models import User
from django.core import mail
from django.core.exceptions import ValidationError
from django.test.client import Client, RequestFactory
from django.test.testcases import TestCase
from nepi.main.forms import CreateAccountForm
from nepi.main.models import Country, School, PendingTeachers
from nepi.main.tests.factories import UserFactory, GroupFactory
from nepi.main.views import RegistrationView


class TestRegistrationView(TestCase):
    def setUp(self):
        self.view = RegistrationView()
        self.existing_user = UserFactory()
        self.client = Client()
        self.factory = RequestFactory()
        self.country = Country(name='LS')
        self.country.save()
        self.school = School(country=self.country, name='School 1')
        self.school.save()
        self.group = GroupFactory()

    def test_duplicate_user(self):
        try:
            form = CreateAccountForm()
            form.cleaned_data = {
                'username': self.existing_user.username
            }
            RegistrationView().form_valid(form)
            self.fail("ValidationException expected")
        except ValidationError:
            pass

    def test_form_valid_success_student(self):
        form = CreateAccountForm()
        form.cleaned_data = {
            'username': 'janedoe21',
            'email': 'janedoe21@ccnmtl.columbia.edu',
            'password1': 'test',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'country': 'LS'
        }
        RegistrationView().form_valid(form)
        user = User.objects.get(username='janedoe21')
        self.assertEquals(user.email, 'janedoe21@ccnmtl.columbia.edu')
        self.assertEquals(user.profile.profile_type, 'ST')
        self.assertEquals(user.first_name, 'Jane')
        self.assertEquals(user.last_name, 'Doe')

        self.assertEquals(user.profile.country.name, 'LS')

        self.assertFalse(user.profile.icap_affil)

        self.assertTrue(Client().login(username='janedoe21', password="test"))

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         'ICAP Nursing E-Learning Registration')

    def test_form_valid_success_faculty(self):
        form = CreateAccountForm()
        form.cleaned_data = {
            'username': 'janedoe21',
            'email': 'janedoe21@ccnmtl.columbia.edu',
            'password1': 'test',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'country': 'LS',
            'profile_type': True,
            'nepi_affiliated': True
        }
        RegistrationView().form_valid(form)
        user = User.objects.get(username='janedoe21')
        self.assertEquals(user.email, 'janedoe21@ccnmtl.columbia.edu')
        self.assertEquals(user.profile.profile_type, 'ST')
        self.assertEquals(user.first_name, 'Jane')
        self.assertEquals(user.last_name, 'Doe')

        self.assertEquals(user.profile.country.name, 'LS')

        self.assertTrue(user.profile.icap_affil)

        self.assertTrue(Client().login(username='janedoe21', password="test"))

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject,
                         'ICAP Nursing E-Learning Registration')
        self.assertEqual(mail.outbox[1].subject,
                         'Nursing E-Learning: Faculty Access Request')

        self.assertEquals(PendingTeachers.objects.all().count(), 1)

    def test_student_registration_view_duplicate(self):
        '''when students are registered they should not be added to pending'''
        response = self.client.post(
            '/register/',
            {"first_name": "regstudent", "last_name": "regstudent",
             "username": self.existing_user.username,
             "email": "test_email@email.com",
             "password1": "test", "password2": "test",
             "country": "LS", "nepi_affiliated": False,
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
             "country": "LS", "nepi_affiliated": False,
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
             "country": "LS", "school": self.school.id,
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
