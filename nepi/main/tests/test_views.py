from datetime import datetime
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, RequestFactory
from django.test.client import Client
from factories import UserFactory, UserProfileFactory, TeacherProfileFactory, \
    ICAPProfileFactory
from nepi.main.forms import ContactForm
from nepi.main.models import UserProfile, Country, School, Group, \
    PendingTeachers
from nepi.main.tests.factories import SchoolFactory, CountryFactory, \
    SchoolGroupFactory, StudentProfileFactory
from nepi.main.views import ContactView, ViewPage, CreateSchoolView
from pagetree.models import UserPageVisit, Section, Hierarchy
from pagetree.tests.factories import ModuleFactory
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
        ModuleFactory("main", "/pages/main/")
        self.h = Hierarchy.objects.get(name='main')

        self.s = self.h.get_root().get_first_leaf()
        self.u = UserFactory(is_superuser=True)
        self.up = UserProfileFactory(user=self.u)
        self.c = Client()
        self.c.login(username=self.u.username, password="test")

    def test_edit_page_form(self):
        r = self.c.get(self.s.get_edit_url())
        self.assertEqual(r.status_code, 200)

    def test_page(self):
        r = self.c.get(self.s.get_absolute_url())
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
        ModuleFactory("main", "/pages/main/")
        self.h = Hierarchy.objects.get(name='main')

        self.s = self.h.get_root().get_first_leaf()
        self.u = UserFactory(is_superuser=True)
        self.up = TeacherProfileFactory(user=self.u)
        self.c = Client()
        self.c.login(username=self.u.username, password="test")

    def test_page(self):
        r = self.c.get(self.s.get_absolute_url())
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
        ModuleFactory("main", "/pages/main/")
        self.h = Hierarchy.objects.get(name='main')

        self.s = self.h.get_root().get_first_leaf()
        self.u = UserFactory(is_superuser=True)
        self.up = ICAPProfileFactory(user=self.u)
        self.c = Client()
        self.c.login(username=self.u.username, password="test")

    def test_page(self):
        r = self.c.get(self.s.get_absolute_url())
        self.assertEqual(r.status_code, 200)

    def test_home(self):
        response = self.c.get("/", follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/icap-dashboard/%d/'
                            % self.up.pk, 302)])
        self.assertTemplateUsed(response, 'dashboard/icap_dashboard.html')


class TestPageView(TestCase):
    def setUp(self):
        self.h = Hierarchy.objects.create(name='main', base_url='/')
        self.h.get_root().add_child_section_from_dict(
            {
                'label': 'Welcome',
                'slug': 'welcome',
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

        request = RequestFactory().get('/%s/' % self.h.name)
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


class TestSchoolChoiceView(TestCase):

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
        response = self.client.get('/schools/XY/', {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 404)

    def test_get_no_schools(self):
        response = self.client.get('/schools/%s/' % self.country.name, {},
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


class TestSchoolGroupChoiceView(TestCase):

    def setUp(self):
        self.user = UserProfileFactory().user
        self.client = Client()
        self.client.login(username=self.user.username, password="test")

    def test_ajax_only(self):
        grp = SchoolGroupFactory()
        response = self.client.get('/groups/%s/' % grp.school.id)
        self.assertEquals(response.status_code, 405)

    def test_get_school_not_found(self):
        response = self.client.get('/groups/782/', {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 404)

    def test_get_no_groups(self):
        school = SchoolFactory()
        response = self.client.get('/groups/%s/' % school.id,
                                   {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEquals(len(the_json['groups']), 0)

    def test_get_groups(self):
        grp = SchoolGroupFactory()

        response = self.client.get('/groups/%s/' % grp.school.id,
                                   {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEquals(len(the_json['groups']), 1)

        self.assertEquals(the_json['groups'][0]['id'], str(grp.id))
        self.assertEquals(the_json['groups'][0]['name'], grp.name)


class TestCreateSchoolView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.country = Country(name='LS')
        self.country.save()
        self.school = School(country=self.country, name='School 1')
        self.school.save()
        self.group = Group(school=self.school,
                           name="Group",
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

    def test_create_school(self):
        '''CreateSchoolView'''
        u = UserFactory()
        request = self.factory.post(
            '/add_school/',
            {"name": "School Needs Name",
             "creator": u,
             "country": self.country})
        request.user = u
        CreateSchoolView.as_view()(request)


class TestConfirmAndDenyFacultyViews(TestCase):
    def setUp(self):
        self.school = SchoolFactory()
        self.icap = ICAPProfileFactory().user
        self.teacher = TeacherProfileFactory().user
        self.pending = StudentProfileFactory().user

        PendingTeachers.objects.create(user_profile=self.pending.profile,
                                       school=self.school)

        self.client = Client()

    def test_ajax_only(self):
        self.client.login(username=self.icap.username, password="test")

        response = self.client.post('/faculty/confirm/', {})
        self.assertEquals(response.status_code, 405)

        response = self.client.post('/faculty/deny/', {})
        self.assertEquals(response.status_code, 405)

    def test_unauthorized(self):
        self.client.login(username=self.teacher.username, password="test")
        response = self.client.post('/faculty/confirm/',
                                    {'user_id': self.pending.id},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 403)

        response = self.client.post('/faculty/deny/',
                                    {'user_id': self.pending.id},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 403)

    def test_confirm_faculty(self):
        self.client.login(username=self.icap.username, password="test")
        response = self.client.post('/faculty/confirm/',
                                    {'user_id': self.pending.id},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        self.pending = User.objects.get(username=self.pending.username)
        self.assertTrue(self.pending.profile.is_teacher())
        self.assertEquals(self.pending.profile.school, self.school)
        self.assertEquals(self.pending.profile.country, self.school.country)

        self.assertEquals(PendingTeachers.objects.count(), 0)
        self.assertEquals(len(mail.outbox), 1)

    def test_deny_faculty(self):
        self.client.login(username=self.icap.username, password="test")

        response = self.client.post('/faculty/deny/',
                                    {'user_id': self.pending.id},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        self.pending = User.objects.get(username=self.pending.username)
        self.assertTrue(self.pending.profile.is_student())

        self.assertEquals(PendingTeachers.objects.count(), 0)
        self.assertEquals(len(mail.outbox), 1)
