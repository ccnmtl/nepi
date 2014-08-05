from django.contrib.auth.models import User
from django.core import mail
from django.test.client import Client
from django.test.testcases import TestCase
from nepi.main.forms import UserProfileForm, CreateAccountForm, \
    UpdateProfileForm
from nepi.main.models import PendingTeachers
from nepi.main.tests.factories import SchoolFactory, StudentProfileFactory, \
    CountryFactory


class TestUserProfileForm(TestCase):

    def setUp(self):
        self.school = SchoolFactory()
        self.student = StudentProfileFactory().user

    def test_clean_errors(self):
        form = UserProfileForm()
        form._errors = {}
        form.cleaned_data = {
            'password1': 'foo',
            'password2': 'bar'
        }

        form.clean()
        self.assertTrue('password1' in form._errors)
        self.assertTrue('password2' in form._errors)
        self.assertTrue('country' in form._errors)

    def test_clean_success(self):
        form = UserProfileForm()
        form._errors = {}
        form.cleaned_data = {
            'password1': 'foo',
            'password2': 'foo',
            'country': self.school.country.name
        }

        form.clean()
        self.assertEquals(len(form._errors.keys()), 0)

    def test_clean_teacher_errors(self):
        form = UserProfileForm()
        form._errors = {}
        form.cleaned_data = {
            'profile_type': True,
            'password1': 'foo',
            'password2': 'foo',
            'country': 'LS'
        }
        form.clean()
        self.assertTrue('email' in form._errors)
        self.assertTrue('school' in form._errors)

    def test_clean_teacher_success(self):
        form = UserProfileForm()
        form._errors = {}
        form.cleaned_data = {
            'profile_type': True,
            'password1': 'foo',
            'password2': 'foo',
            'country': self.school.country.name,
            'email': 'jdoe@foo.bar',
            'school': self.school.id
        }
        form.clean()
        self.assertEquals(len(form._errors.keys()), 0)

    def test_create_pending_teacher(self):
        form = UserProfileForm()
        form.create_pending_teacher(self.student, self.school.id)
        self.assertEquals(PendingTeachers.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_send_success_email(self):
        form = UserProfileForm(self.student)
        form.send_success_email(self.student)
        self.assertEqual(len(mail.outbox), 1)


class TestCreateAccountForm(TestCase):
    def setUp(self):
        self.country = CountryFactory()
        self.school = SchoolFactory()
        self.student = StudentProfileFactory().user

    def test_clean_duplicateuser(self):
        form = CreateAccountForm()
        form._errors = {}
        form.cleaned_data = {
            'password1': 'foo',
            'password2': 'foo',
            'country': self.school.country.name,
            'username': self.student.username
        }

        form.clean()
        self.assertEquals(len(form._errors.keys()), 1)
        self.assertTrue('username' in form._errors)

    def test_save_success_student(self):
        form = CreateAccountForm()
        form.cleaned_data = {
            'username': 'janedoe21',
            'email': 'janedoe21@ccnmtl.columbia.edu',
            'password1': 'test',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'country': self.country.name
        }
        form.save()
        user = User.objects.get(username='janedoe21')
        self.assertEquals(user.email, 'janedoe21@ccnmtl.columbia.edu')
        self.assertEquals(user.profile.profile_type, 'ST')
        self.assertEquals(user.first_name, 'Jane')
        self.assertEquals(user.last_name, 'Doe')

        self.assertEquals(user.profile.country, self.country)

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
            'country': self.school.country.name,
            'school': self.school.id,
            'profile_type': True,
            'nepi_affiliated': True
        }
        form.save()
        user = User.objects.get(username='janedoe21')
        self.assertEquals(user.email, 'janedoe21@ccnmtl.columbia.edu')
        self.assertEquals(user.profile.profile_type, 'ST')
        self.assertEquals(user.first_name, 'Jane')
        self.assertEquals(user.last_name, 'Doe')

        self.assertEquals(user.profile.country, self.school.country)

        self.assertTrue(user.profile.icap_affil)

        self.assertTrue(Client().login(username='janedoe21', password="test"))

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject,
                         'ICAP Nursing E-Learning Registration')
        self.assertEqual(mail.outbox[1].subject,
                         'Nursing E-Learning: Faculty Access Request')

        self.assertEquals(PendingTeachers.objects.all().count(), 1)


class TestUpdateProfileForm(TestCase):
    def setUp(self):
        self.country = CountryFactory()
        self.school = SchoolFactory()
        self.student = StudentProfileFactory().user

    def test_init(self):
        form = UpdateProfileForm(instance=self.student)
        self.assertEquals(form.initial['first_name'], self.student.first_name)
        self.assertEquals(form.initial['last_name'], self.student.last_name)
        self.assertEquals(form.initial['email'], self.student.email)
        self.assertEquals(form.initial['username'], self.student.username)

        self.assertEquals(form.initial['country'],
                          self.student.profile.country.name)
        self.assertFalse('school' in form.initial)
        self.assertEquals(form.initial['nepi_affiliated'],
                          self.student.profile.icap_affil)

    def test_save_success_student(self):
        form = UpdateProfileForm(instance=self.student)
        form.cleaned_data = {
            'username': self.student.username,
            'email': 'janedoe21@ccnmtl.columbia.edu',
            'password1': 'changed',
            'password2': 'changed',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'country': self.country.name,
            'nepi_affiliated': True

        }
        form.save()

        user = User.objects.get(username=self.student.username)
        self.assertEquals(user.email, 'janedoe21@ccnmtl.columbia.edu')
        self.assertEquals(user.profile.profile_type, 'ST')
        self.assertEquals(user.first_name, 'Jane')
        self.assertEquals(user.last_name, 'Doe')
        self.assertEquals(user.profile.country, self.country)
        self.assertTrue(user.profile.icap_affil)

        self.assertTrue(Client().login(username=self.student.username,
                                       password="changed"))

    def test_form_valid_success_faculty(self):
        form = UpdateProfileForm()
        form.cleaned_data = {
            'username': self.student.username,
            'email': 'janedoe21@ccnmtl.columbia.edu',
            'password1': 'test',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'country': self.school.country.name,
            'school': self.school.id,
            'profile_type': True,
            'nepi_affiliated': False
        }
        form.save()
        user = User.objects.get(username=self.student.username)
        self.assertEquals(user.email, 'janedoe21@ccnmtl.columbia.edu')
        self.assertEquals(user.profile.profile_type, 'ST')
        self.assertEquals(user.first_name, 'Jane')
        self.assertEquals(user.last_name, 'Doe')
        self.assertEquals(user.profile.country, self.school.country)
        self.assertFalse(user.profile.icap_affil)

        self.assertTrue(Client().login(username=self.student.username,
                                       password="test"))

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         'Nursing E-Learning: Faculty Access Request')

        self.assertEquals(PendingTeachers.objects.all().count(), 1)
