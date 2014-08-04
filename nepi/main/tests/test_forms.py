from django.test.testcases import TestCase
from nepi.main.forms import CreateAccountForm


class TestCreateAccountForm(TestCase):

    def test_clean_errors(self):
        form = CreateAccountForm()
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
        form = CreateAccountForm()
        form._errors = {}
        form.cleaned_data = {
            'password1': 'foo',
            'password2': 'foo',
            'country': 'LS'
        }

        form.clean()
        self.assertEquals(len(form._errors.keys()), 0)

    def test_clean_teacher_errors(self):
        form = CreateAccountForm()
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
        form = CreateAccountForm()
        form._errors = {}
        form.cleaned_data = {
            'profile_type': True,
            'password1': 'foo',
            'password2': 'foo',
            'country': 'LS',
            'email': 'jdoe@foo.bar',
            'school': 0
        }
        form.clean()
        self.assertEquals(len(form._errors.keys()), 0)
