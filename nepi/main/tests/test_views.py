from django.contrib.auth.models import User
from django.core import mail
from django.core.exceptions import ValidationError
from django.test import TestCase, RequestFactory
from django.test.client import Client
from factories import UserFactory, HierarchyFactory, UserProfileFactory, \
    TeacherProfileFactory, ICAPProfileFactory
from nepi.main.forms import CreateAccountForm, ContactForm
from nepi.main.models import UserProfile, Country, PendingTeachers
from nepi.main.tests.factories import SchoolFactory, CountryFactory
from nepi.main.views import ContactView, ViewPage, RegistrationView
from pagetree.models import UserPageVisit, Section
import json


class TestBasicViews(TestCase):

    def setUp(self):
        self.c = Client()
        self.factory = RequestFactory()
        # ICAP User
        self.icap_user = User.objects.create_user(
            'icap_user', 'icap@icap.com', 'icap_user')
        self.icap_user.save()
        self.country = Country(name='AO')
        self.country.save()
        self.user_profile = UserProfile(
            user=self.icap_user, profile_type='IC', country=self.country)
        self.user_profile.save()

    def test_home(self):
        response = self.c.get("/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.redirect_chain[0],
                          ('http://testserver/accounts/login/?next=/',
                           302))

    def test_about(self):
        response = self.c.get("/about/")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('flatpages/about.html')

    def test_help(self):
        response = self.c.get("/help/")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('flatpages/help.html')

    def test_contact(self):
        request = self.factory.post('/contact/',
                                    {"subject": "new_student",
                                     "message": "new_student",
                                     "sender": "new_student"})
        response = ContactView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_contact_form_valid(self):
        form = ContactForm()
        form.cleaned_data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'sender': 'janedoe21@ccnmtl.columbia.edu',
            'subject': 'Lorem Ipsum',
            'message': 'Proin tristique volutpat purus sed accumsan.'
        }
        ContactView().form_valid(form)
        self.assertEqual(len(mail.outbox), 1)

    def test_smoketest(self):
        response = self.c.get("/smoketest/")
        self.assertEquals(response.status_code, 200)

    def test_register_form(self):
        r = self.c.get("/register/")
        self.assertEqual(r.status_code, 200)

    def test_register_form_invalid_submission(self):
        r = self.c.post("/register/", dict())
        self.assertEqual(r.status_code, 200)


class TestStudentLoggedInViews(TestCase):
    '''go through some of the views student sees'''
    def setUp(self):
        self.h = HierarchyFactory()
        self.s = self.h.get_root().get_first_leaf()
        self.u = UserFactory(is_superuser=True)
        self.up = UserProfileFactory(user=self.u)
        self.c = Client()
        self.c.login(username=self.u.username, password="test")

    def test_edit_page_form(self):
        r = self.c.get("/pages/%s/edit/%s/" % (self.h.name, self.s.slug))
        self.assertEqual(r.status_code, 200)

    def test_page(self):
        r = self.c.get("/pages/%s/%s/" % (self.h.name, self.s.slug))
        self.assertEqual(r.status_code, 200)

    def test_home(self):
        response = self.c.get("/", follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/student-dashboard/%d/'
                            % self.up.pk, 302)])
        self.assertTemplateUsed(response, 'dashboard/icap_dashboard.html')


class TestTeacherLoggedInViews(TestCase):
    '''go through some of the views student sees'''
    def setUp(self):
        self.h = HierarchyFactory()
        self.s = self.h.get_root().get_first_leaf()
        self.u = UserFactory(is_superuser=True)
        self.up = TeacherProfileFactory(user=self.u)
        self.c = Client()
        self.c.login(username=self.u.username, password="test")

    def test_page(self):
        r = self.c.get("/pages/%s/%s/" % (self.h.name, self.s.slug))
        self.assertEqual(r.status_code, 200)

    def test_home(self):
        response = self.c.get("/", follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/faculty-dashboard/%d/'
                            % self.up.pk, 302)])
        self.assertTemplateUsed(response, 'dashboard/icap_dashboard.html')


class TestICAPLoggedInViews(TestCase):
    '''go through some of the views student sees'''
    def setUp(self):
        self.h = HierarchyFactory()
        self.s = self.h.get_root().get_first_leaf()
        self.u = UserFactory(is_superuser=True)
        self.up = ICAPProfileFactory(user=self.u)
        self.c = Client()
        self.c.login(username=self.u.username, password="test")

    def test_page(self):
        r = self.c.get("/pages/%s/%s/" % (self.h.name, self.s.slug))
        self.assertEqual(r.status_code, 200)

    def test_home(self):
        response = self.c.get("/", follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/icap-dashboard/%d/'
                            % self.up.pk, 302)])
        self.assertTemplateUsed(response, 'dashboard/icap_dashboard.html')


class TestRegistrationView(TestCase):
    def setUp(self):
        self.view = RegistrationView()
        self.existing_user = UserFactory()

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
            'country': 'BF'
        }
        RegistrationView().form_valid(form)
        user = User.objects.get(username='janedoe21')
        self.assertEquals(user.email, 'janedoe21@ccnmtl.columbia.edu')
        self.assertEquals(user.profile.profile_type, 'ST')
        self.assertEquals(user.first_name, 'Jane')
        self.assertEquals(user.last_name, 'Doe')

        country = Country.objects.get(name='BF')
        self.assertEquals(user.profile.country, country)

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
            'country': 'BF',
            'profile_type': True
        }
        RegistrationView().form_valid(form)
        user = User.objects.get(username='janedoe21')
        self.assertEquals(user.email, 'janedoe21@ccnmtl.columbia.edu')
        self.assertEquals(user.profile.profile_type, 'ST')
        self.assertEquals(user.first_name, 'Jane')
        self.assertEquals(user.last_name, 'Doe')

        country = Country.objects.get(name='BF')
        self.assertEquals(user.profile.country, country)

        self.assertTrue(Client().login(username='janedoe21', password="test"))

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject,
                         'ICAP Nursing E-Learning Registration')
        self.assertEqual(mail.outbox[1].subject,
                         'Nursing E-Learning: Faculty Access Request')

        self.assertEquals(PendingTeachers.objects.all().count(), 1)


class TestPageView(TestCase):
    def setUp(self):
        self.h = HierarchyFactory()
        self.h.get_root().add_child_section_from_dict(
            {
                'label': 'Page One',
                'slug': 'page-one',
                'pageblocks': [
                    {'label': 'Introduction',
                     'css_extra': '',
                     'block_type': 'Text Block',
                     'body': 'random text goes here',
                     },
                ],
                'children': [],
            })
        self.h.get_root().add_child_section_from_dict(
            {
                'label': 'Page Two',
                'slug': 'page-two',
                'pageblocks': [
                    {'label': 'Content',
                     'css_extra': '',
                     'block_type': 'Text Block',
                     'body': 'random text goes here',
                     },
                ],
                'children': [],
            })

        self.s = self.h.get_root().get_first_leaf()
        self.u = UserFactory(is_superuser=True)
        self.up = UserProfileFactory(user=self.u)
        self.c = Client()
        self.c.login(username=self.u.username, password="test")

    def test_get_extra_context(self):
        section_one = Section.objects.get(slug='welcome')
        section_two = Section.objects.get(slug='page-one')
        section_three = Section.objects.get(slug='page-two')

        request = RequestFactory().get('/pages/%s/' % self.h.name)
        request.user = self.u

        view = ViewPage()
        view.request = request
        view.root = self.h.get_root()

        ctx = view.get_extra_context()
        self.assertTrue('menu' in ctx)
        self.assertEquals(len(ctx['menu']), 3)

        self.assertEquals(ctx['menu'][0]['id'], section_one.id)
        self.assertFalse(ctx['menu'][0]['disabled'])
        self.assertEquals(ctx['menu'][0]['label'], 'Welcome')
        self.assertEquals(ctx['menu'][0]['url'], u'/welcome/')
        self.assertEquals(ctx['menu'][0]['depth'], 2)

        self.assertEquals(ctx['menu'][1]['id'], section_two.id)
        self.assertTrue(ctx['menu'][1]['disabled'])
        self.assertEquals(ctx['menu'][2]['id'], section_three.id)
        self.assertTrue(ctx['menu'][2]['disabled'])

        UserPageVisit.objects.create(user=self.u,
                                     section=section_one,
                                     status='complete')
        ctx = view.get_extra_context()
        self.assertEquals(ctx['menu'][0]['id'], section_one.id)
        self.assertFalse(ctx['menu'][0]['disabled'])
        self.assertEquals(ctx['menu'][1]['id'], section_two.id)
        self.assertFalse(ctx['menu'][1]['disabled'])
        self.assertEquals(ctx['menu'][2]['id'], section_three.id)
        self.assertTrue(ctx['menu'][2]['disabled'])


class TestSchoolView(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.up = UserProfileFactory(user=self.user)
        self.client = Client()
        self.client.login(username=self.user.username, password="test")
        self.country = CountryFactory()
        self.school = SchoolFactory()

    def test_ajax_only(self):
        response = self.client.get('/schools/%s/' % self.school.country.name)
        self.assertEquals(response.status_code, 405)

    def test_get_country_not_found(self):
        response = self.client.get('/schools/XY/',
                                   {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 404)

    def test_get_no_schools(self):
        response = self.client.get('/schools/%s/' % self.country.name,
                                   {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEquals(len(the_json['schools']), 1)
        self.assertEquals(the_json['schools'][0]['id'], '-----')
        self.assertEquals(the_json['schools'][0]['name'], '-----')

    def test_get_schools(self):
        response = self.client.get('/schools/%s/' % self.school.country.name,
                                   {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEquals(len(the_json['schools']), 2)

        self.assertEquals(the_json['schools'][0]['id'], '-----')
        self.assertEquals(the_json['schools'][0]['name'], '-----')
        self.assertEquals(the_json['schools'][1]['id'], str(self.school.id))
        self.assertEquals(the_json['schools'][1]['name'], self.school.name)
