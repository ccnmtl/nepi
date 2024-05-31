from __future__ import unicode_literals

from datetime import datetime
from json import loads
import json

from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.core import mail
from django.core.cache import cache
from django.test import TestCase, RequestFactory
from django.test.client import Client
from django.urls.base import reverse
from django.utils.translation import get_language
from pagetree.models import UserPageVisit, Section, Hierarchy
from pagetree.tests.factories import ModuleFactory

from nepi.main.forms import ContactForm
from nepi.main.models import Country, School, Group, PendingTeachers
from nepi.main.tests.factories import (
    UserFactory, UserProfileFactory, ICAPProfileFactory
)
from nepi.main.tests.factories import SchoolFactory, CountryFactory, \
    SchoolGroupFactory, StudentProfileFactory, \
    CountryAdministratorProfileFactory, \
    InstitutionAdminProfileFactory, PendingTeacherFactory, \
    TeacherProfileFactory
from nepi.main.views import ContactView, CreateSchoolView, \
    UserProfileView, PeopleView, PeopleFilterView, RosterDetail, GroupDetail, \
    StudentGroupDetail, NepiPageView
LANGUAGE_SESSION_KEY = '_language'


class TestBasicViews(TestCase):

    def test_home(self):
        response = self.client.get("/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[0],
                         ('/accounts/login/?next=/', 302))

    def test_contact(self):
        response = self.client.post(reverse('contactus'),
                                    {"subject": "new_student",
                                     "message": "new_student",
                                     "sender": "new_student"})
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
        view = ContactView()
        view.request = RequestFactory().get(reverse('contactus'))
        view.request.user = AnonymousUser()

        view.form_valid(form)
        self.assertEqual(len(mail.outbox), 1)

    def test_smoketest(self):
        response = self.client.get("/smoketest/")
        self.assertEqual(response.status_code, 200)

    def test_edit_page_form(self):
        staff = ICAPProfileFactory().user
        staff.is_staff = True
        staff.save()

        ModuleFactory("optionb-en", "/pages/optionb/en/")
        hierarchy = Hierarchy.objects.get(name='optionb-en')
        section = hierarchy.get_root().get_first_leaf()

        self.client.login(username=staff.username, password="test")
        response = self.client.get(section.get_edit_url())
        self.assertEqual(response.status_code, 200)


class TestStudentLoggedInViews(TestCase):
    '''go through some of the views student sees'''
    def setUp(self):
        ModuleFactory("optionb-en", "/pages/optionb/en/")
        self.hierarchy = Hierarchy.objects.get(name='optionb-en')
        self.section = self.hierarchy.get_root().get_first_leaf()

        self.student = StudentProfileFactory().user
        self.client.login(username=self.student.username, password="test")

    def test_edit_page_form(self):
        response = self.client.get(self.section.get_edit_url())
        self.assertEqual(response.status_code, 302)

    def test_page(self):
        response = self.client.get(self.section.get_absolute_url(),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain,
                         [('/pages/optionb/en/one/', 302)])

    def test_deprecated_page(self):
        response = self.client.get('/pages/main/one/',
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain,
                         [('/pages/optionb/en/one/', 302)])

    def test_home(self):
        response = self.client.get("/", follow=True)
        self.assertEqual(response.redirect_chain,
                         [('/dashboard/#user-modules', 302)])
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')

    def test_home_noprofile(self):
        user = UserFactory()
        self.client.login(username=user.username, password="test")

        response = self.client.get("/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[0],
                         ('/register/', 302))

    def test_dashboard(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_context(self):
        request = RequestFactory().get(reverse('dashboard'))
        request.user = self.student

        view = UserProfileView()
        view.request = request

        self.assertEqual(view.get_object(), request.user.profile)

        view.object = request.user.profile
        ctx = view.get_context_data()

        self.assertEqual(ctx['optionb'], self.hierarchy)
        self.assertIsNotNone(ctx['profile_form'])
        self.assertEqual(ctx['countries'], Country.choices())
        self.assertEqual(ctx['joined_groups'].count(), 0)
        self.assertTrue('managed_groups' not in ctx)
        self.assertTrue('pending_teachers' not in ctx)

    def update_user_language(self, language):
        data = {u'username': [self.student.username],
                u'password1': [u''],
                u'first_name': [self.student.first_name],
                u'last_name': [self.student.last_name],
                u'language': [language],
                u'country': [self.student.profile.country.name],
                u'password2': [u''],
                u'nepi_affiliated': [u'off'],
                u'email': [self.student.email]}

        response = self.client.post(reverse('dashboard'), data)
        self.assertEqual(response.status_code, 302)

    def test_dashboard_post_change_language(self):
        self.assertEqual(self.student.profile.language,
                         settings.DEFAULT_LANGUAGE)
        self.assertEqual(get_language(), 'en')
        self.assertEqual(self.client.session[LANGUAGE_SESSION_KEY], 'en')

        self.update_user_language(u'pt')
        student = User.objects.get(id=self.student.id)
        self.assertEqual(student.profile.language, 'pt')
        self.assertEqual(get_language(), 'pt')
        self.assertEqual(self.client.session[LANGUAGE_SESSION_KEY], 'pt')


class TestTeacherLoggedInViews(TestCase):

    def setUp(self):
        ModuleFactory("optionb-en", "/pages/optionb/en/")
        self.hierarchy = Hierarchy.objects.get(name='optionb-en')
        self.section = self.hierarchy.get_root().get_first_leaf()

        self.teacher = TeacherProfileFactory().user
        self.client = Client()
        self.client.login(username=self.teacher.username, password="test")

    def test_page(self):
        response = self.client.get(self.section.get_absolute_url(),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain,
                         [('/pages/optionb/en/one/', 302)])

    def test_home(self):
        response = self.client.get("/", follow=True)
        self.assertEqual(response.redirect_chain,
                         [('/dashboard/#user-groups', 302)])
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')

    def test_dashboard(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_context(self):
        request = RequestFactory().get('/dashboard/')
        request.user = self.teacher

        school_group = SchoolGroupFactory(creator=self.teacher,
                                          school=self.teacher.profile.school)

        # archived group
        SchoolGroupFactory(creator=self.teacher,
                           school=self.teacher.profile.school,
                           archived=True)
        # alt_creator
        SchoolGroupFactory(creator=TeacherProfileFactory().user)

        view = UserProfileView()
        view.request = request

        self.assertEqual(view.get_object(), request.user.profile)

        view.object = request.user.profile
        ctx = view.get_context_data()

        self.assertEqual(ctx['optionb'], self.hierarchy)
        self.assertIsNotNone(ctx['profile_form'])
        self.assertEqual(ctx['countries'], Country.choices())
        self.assertEqual(ctx['joined_groups'].count(), 0)
        self.assertEqual(len(ctx['managed_groups']), 1)
        self.assertEqual(ctx['managed_groups'][0], school_group)
        self.assertTrue('pending_teachers' not in ctx)


class TestInstitutionAdminLoggedInViews(TestCase):

    def setUp(self):
        ModuleFactory("optionb-en", "/pages/optionb/en/")
        self.hierarchy = Hierarchy.objects.get(name='optionb-en')
        self.section = self.hierarchy.get_root().get_first_leaf()

        self.admin = InstitutionAdminProfileFactory().user
        self.client = Client()
        self.client.login(username=self.admin.username, password="test")

        self.teacher = TeacherProfileFactory(
            school=self.admin.profile.school).user

    def test_page(self):
        response = self.client.get(self.section.get_absolute_url(),
                                   follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain,
                         [('/pages/optionb/en/one/', 302)])

    def test_home(self):
        response = self.client.get("/", follow=True)
        self.assertEqual(response.redirect_chain,
                         [('/dashboard/#user-groups', 302)])
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')

    def test_dashboard(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_context(self):
        request = RequestFactory().get('/dashboard/')
        request.user = self.admin

        admin_group = SchoolGroupFactory(creator=self.admin,
                                         school=self.admin.profile.school)
        teacher_group = SchoolGroupFactory(creator=self.teacher,
                                           school=self.teacher.profile.school)

        # archived groups
        SchoolGroupFactory(creator=self.teacher,
                           school=self.teacher.profile.school,
                           archived=True)
        SchoolGroupFactory(creator=self.admin,
                           school=self.admin.profile.school,
                           archived=True)

        # alt_creator/alt school
        SchoolGroupFactory(creator=TeacherProfileFactory().user)

        view = UserProfileView()
        view.request = request

        self.assertEqual(view.get_object(), request.user.profile)

        view.object = request.user.profile
        ctx = view.get_context_data()

        self.assertEqual(ctx['optionb'], self.hierarchy)
        self.assertIsNotNone(ctx['profile_form'])
        self.assertEqual(ctx['countries'], Country.choices())
        self.assertEqual(ctx['joined_groups'].count(), 0)
        self.assertEqual(len(ctx['managed_groups']), 2)
        self.assertEqual(ctx['managed_groups'][0], admin_group)
        self.assertEqual(ctx['managed_groups'][1], teacher_group)

        # pending teachers
        PendingTeacherFactory()  # random country/school
        alt_school = SchoolFactory(country=self.admin.profile.country)
        PendingTeacherFactory(school=alt_school)  # same country, diff school
        pt = PendingTeacherFactory(school=self.admin.profile.school)  # visible
        self.assertEqual(len(ctx['pending_teachers']), 1)
        self.assertEqual(ctx['pending_teachers'][0], pt)


class TestCountryAdminLoggedInViews(TestCase):

    def setUp(self):
        ModuleFactory("optionb-en", "/pages/optionb/en/")
        self.hierarchy = Hierarchy.objects.get(name='optionb-en')
        self.section = self.hierarchy.get_root().get_first_leaf()

        self.school = SchoolFactory()
        self.country = self.school.country
        self.alt_school = SchoolFactory(country=self.country)

        self.teacher = TeacherProfileFactory(school=self.school).user
        self.iadmin = InstitutionAdminProfileFactory(
            school=self.alt_school).user
        self.admin = CountryAdministratorProfileFactory(
            country=self.country).user

        self.client = Client()
        self.client.login(username=self.admin.username, password="test")

    def test_page(self):
        response = self.client.get(self.section.get_absolute_url(),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain,
                         [('/pages/optionb/en/one/', 302)])

    def test_home(self):
        response = self.client.get("/", follow=True)
        self.assertEqual(response.redirect_chain,
                         [('/dashboard/#user-groups', 302)])
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')

    def test_dashboard(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_context(self):
        request = RequestFactory().get('/dashboard/')
        request.user = self.admin

        admin_group = SchoolGroupFactory(creator=self.admin,
                                         school=self.school)
        iadmin_group = SchoolGroupFactory(creator=self.iadmin,
                                          school=self.iadmin.profile.school)
        teacher_group = SchoolGroupFactory(creator=self.teacher,
                                           school=self.teacher.profile.school)

        # archived groups
        SchoolGroupFactory(creator=self.teacher,
                           school=self.teacher.profile.school,
                           archived=True)
        SchoolGroupFactory(creator=self.admin, school=self.school,
                           archived=True)

        # random groups alt_creator/alt school groups
        SchoolGroupFactory(creator=TeacherProfileFactory().user)

        view = UserProfileView()
        view.request = request

        self.assertEqual(view.get_object(), request.user.profile)

        view.object = request.user.profile
        ctx = view.get_context_data()

        self.assertEqual(ctx['optionb'], self.hierarchy)
        self.assertIsNotNone(ctx['profile_form'])
        self.assertEqual(ctx['countries'], Country.choices())
        self.assertEqual(ctx['joined_groups'].count(), 0)
        self.assertEqual(len(ctx['managed_groups']), 3)
        self.assertTrue(admin_group in ctx['managed_groups'])
        self.assertTrue(teacher_group in ctx['managed_groups'])
        self.assertTrue(iadmin_group in ctx['managed_groups'])

        # pending teachers
        PendingTeacherFactory()  # random country/school
        pt1 = PendingTeacherFactory(school=self.alt_school)
        pt2 = PendingTeacherFactory(school=self.school)  # visible
        self.assertEqual(len(ctx['pending_teachers']), 2)
        self.assertTrue(pt2 in ctx['pending_teachers'])
        self.assertTrue(pt1 in ctx['pending_teachers'])


class TestICAPLoggedInViews(TestCase):

    def setUp(self):
        ModuleFactory("optionb-en", "/pages/optionb/en/")
        self.hierarchy = Hierarchy.objects.get(name='optionb-en')
        self.section = self.hierarchy.get_root().get_first_leaf()

        self.icap = ICAPProfileFactory().user
        self.client = Client()
        self.client.login(username=self.icap.username, password="test")

    def test_page(self):
        response = self.client.get(self.section.get_absolute_url(),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain,
                         [('/pages/optionb/en/one/', 302)])

    def test_home(self):
        response = self.client.get("/", follow=True)
        self.assertEqual(response.redirect_chain,
                         [('/dashboard/#user-groups', 302)])
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')

    def test_dashboard(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_context(self):
        request = RequestFactory().get('/dashboard/')
        request.user = self.icap

        a = SchoolGroupFactory()
        b = SchoolGroupFactory()
        SchoolGroupFactory(archived=True)

        view = UserProfileView()
        view.request = request

        self.assertEqual(view.get_object(), request.user.profile)

        view.object = request.user.profile
        ctx = view.get_context_data()

        self.assertEqual(ctx['optionb'], self.hierarchy)
        self.assertIsNotNone(ctx['profile_form'])
        self.assertEqual(ctx['countries'], Country.choices())
        self.assertEqual(ctx['joined_groups'].count(), 0)
        self.assertEqual(len(ctx['managed_groups']), 2)
        self.assertTrue(a in ctx['managed_groups'])
        self.assertTrue(b in ctx['managed_groups'])

        # pending teachers
        pt = PendingTeacherFactory()  # random country/school
        self.assertEqual(len(ctx['pending_teachers']), 1)
        self.assertEqual(ctx['pending_teachers'][0], pt)


class TestPageView(TestCase):
    def setUp(self):
        cache.clear()
        self.h = Hierarchy.objects.create(name='optionb-en', base_url='/')
        self.h.get_root().add_child_section_from_dict(
            {
                'label': 'Welcome',
                'slug': 'welcome',
                'pageblocks': [
                    {
                        'label': 'Introduction',
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
                    {
                        'label': 'Introduction',
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
                    {
                        'label': 'Content',
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

        view = NepiPageView()
        view.request = request
        view.root = self.h.get_root()

        ctx = view.get_extra_context()
        self.assertTrue('menu' in ctx)
        self.assertEqual(len(ctx['menu']), 3)

        self.assertEqual(ctx['menu'][0]['id'], section_one.id)
        self.assertFalse(ctx['menu'][0]['disabled'])
        self.assertEqual(ctx['menu'][0]['label'], 'Welcome')
        self.assertEqual(ctx['menu'][0]['url'], u'/welcome/')
        self.assertEqual(ctx['menu'][0]['depth'], 2)

        self.assertEqual(ctx['menu'][1]['id'], section_two.id)
        self.assertTrue(ctx['menu'][1]['disabled'])
        self.assertEqual(ctx['menu'][2]['id'], section_three.id)
        self.assertTrue(ctx['menu'][2]['disabled'])

        UserPageVisit.objects.create(user=self.u,
                                     section=section_one,
                                     status='complete')
        ctx = view.get_extra_context()
        self.assertEqual(ctx['menu'][0]['id'], section_one.id)
        self.assertFalse(ctx['menu'][0]['disabled'])
        self.assertEqual(ctx['menu'][1]['id'], section_two.id)
        self.assertFalse(ctx['menu'][1]['disabled'])
        self.assertEqual(ctx['menu'][2]['id'], section_three.id)
        self.assertTrue(ctx['menu'][2]['disabled'])


class TestSchoolChoiceView(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.up = UserProfileFactory(user=self.user)
        self.client = Client()
        self.client.login(username=self.user.username, password="test")
        self.country = CountryFactory()
        self.school = SchoolFactory()

    def test_get_country_not_found(self):
        response = self.client.get('/schools/11/', {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)

    def test_get_no_schools(self):
        response = self.client.get('/schools/%s/' % self.country.name, {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEqual(len(the_json['schools']), 0)

    def test_get_schools(self):
        response = self.client.get('/schools/%s/' % self.school.country.name,
                                   {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEqual(len(the_json['schools']), 1)

        self.assertEqual(the_json['schools'][0]['id'], str(self.school.id))
        self.assertEqual(the_json['schools'][0]['name'], self.school.name)


class TestSchoolGroupChoiceView(TestCase):

    def setUp(self):
        self.user = TeacherProfileFactory().user
        self.client = Client()
        self.client.login(username=self.user.username, password="test")

    def test_get_school_not_found(self):
        response = self.client.post('/groups/782/', {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)

    def test_get_no_groups(self):
        school = SchoolFactory()
        response = self.client.post('/groups/%s/' % school.id,
                                    {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEqual(len(the_json['groups']), 0)

    def test_get_groups(self):
        grp = SchoolGroupFactory()

        response = self.client.post('/groups/%s/' % grp.school.id,
                                    {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEqual(len(the_json['groups']), 1)

        self.assertEqual(the_json['groups'][0]['id'], str(grp.id))
        self.assertEqual(the_json['groups'][0]['name'], grp.name)

    def test_get_visible_groups(self):
        school = SchoolFactory()
        joined = SchoolGroupFactory(school=school)
        joined.userprofile_set.add(self.user.profile)
        SchoolGroupFactory(archived=True, school=school)  # archived
        SchoolGroupFactory(creator=self.user, school=school)  # created

        grp = SchoolGroupFactory(school=school)

        response = self.client.post('/groups/%s/' % school.id,
                                    {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEqual(len(the_json['groups']), 1)

        self.assertEqual(the_json['groups'][0]['id'], str(grp.id))
        self.assertEqual(the_json['groups'][0]['name'], grp.name)

    def test_get_managed_groups(self):
        school = self.user.profile.school
        joined = SchoolGroupFactory(school=school)
        joined.userprofile_set.add(self.user.profile)
        SchoolGroupFactory(archived=True, school=school)  # archived
        SchoolGroupFactory(school=school)  # random group

        created = SchoolGroupFactory(creator=self.user, school=school)

        response = self.client.post('/groups/%s/' % school.id,
                                    {'managed': True},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEqual(len(the_json['groups']), 1)

        self.assertEqual(the_json['groups'][0]['id'], str(created.id))
        self.assertEqual(the_json['groups'][0]['name'], created.name)


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
        u = TeacherProfileFactory().user
        request = self.factory.post(
            '/add_school/',
            {"name": "School Needs Name",
             "creator": u,
             "country": self.country})
        request.user = u
        CreateSchoolView.as_view()(request)


class TestUpdateGroupView(TestCase):
    def setUp(self):
        self.student = StudentProfileFactory().user
        self.creator = TeacherProfileFactory().user
        self.teacher = TeacherProfileFactory().user

        self.group = SchoolGroupFactory(creator=self.creator)

    def test_access(self):
        # not logged in
        response = self.client.post('/edit_group/', {})
        self.assertEqual(response.status_code, 302)

        # not authorized
        self.client.login(username=self.student.username, password="test")
        response = self.client.post('/edit_group/', {'pk': self.group.id})
        self.assertEqual(response.status_code, 403)

        # not authorized
        self.client.login(username=self.teacher.username, password="test")
        response = self.client.post('/edit_group/', {'pk': self.group.id})
        self.assertEqual(response.status_code, 403)

        # invalid method
        self.client.login(username=self.creator.username, password="test")
        response = self.client.get('/edit_group/')
        self.assertEqual(response.status_code, 405)

        # required data not available
        self.client.login(username=self.creator.username, password="test")
        response = self.client.post('/edit_group/', {})
        self.assertEqual(response.status_code, 404)

    def test_post(self):
        self.client.login(username=self.creator.username, password="test")
        response = self.client.post('/edit_group/',
                                    {'pk': self.group.id,
                                     'name': 'New Group',
                                     'start_date': '01/01/2015',
                                     'end_date': '01/05/2015'})
        self.assertEqual(response.status_code, 302)

        # refresh from database
        group = Group.objects.get(id=self.group.id)
        self.assertEqual(group.name, 'New Group')
        self.assertEqual(str(group.start_date), '2015-01-01')
        self.assertEqual(str(group.end_date), '2015-01-05')


class TestJoinGroupView(TestCase):
    def setUp(self):
        self.student = StudentProfileFactory().user
        self.group = SchoolGroupFactory()

    def test_access(self):
        # not logged in
        response = self.client.post('/join_group/', {})
        self.assertEqual(response.status_code, 302)

        # method not authorized
        self.client.login(username=self.student.username, password="test")
        response = self.client.get('/join_group/')
        self.assertEqual(response.status_code, 405)

        # invalid data
        response = self.client.post('/join_group/', {})
        self.assertEqual(response.status_code, 404)

    def test_join_group(self):
        self.assertEqual(self.student.profile.group.count(), 0)

        self.client.login(username=self.student.username, password="test")
        response = self.client.post('/join_group/', {'group': self.group.id})
        self.assertEqual(response.status_code, 302)

        self.assertEqual(self.student.profile.group.count(), 1)


class TestDeleteGroupView(TestCase):
    def setUp(self):
        self.student = StudentProfileFactory().user
        self.creator = TeacherProfileFactory().user
        self.teacher = TeacherProfileFactory().user

        self.group = SchoolGroupFactory(creator=self.creator)

    def test_access(self):
        # not logged in
        response = self.client.post('/delete_group/', {})
        self.assertEqual(response.status_code, 302)

        # not authorized
        self.client.login(username=self.student.username, password="test")
        response = self.client.post('/delete_group/', {'group': self.group.id})
        self.assertEqual(response.status_code, 403)

        # not authorized
        self.client.login(username=self.teacher.username, password="test")
        response = self.client.post('/delete_group/', {'group': self.group.id},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)

        # invalid method
        self.client.login(username=self.creator.username, password="test")
        response = self.client.get('/delete_group/')
        self.assertEqual(response.status_code, 405)

        # required data not available
        self.client.login(username=self.creator.username, password="test")
        response = self.client.post('/delete_group/', {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)

    def test_post(self):
        self.client.login(username=self.creator.username, password="test")
        response = self.client.post('/delete_group/', {'group': self.group.id},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(loads(response.content)['success'])

        with self.assertRaises(Group.DoesNotExist):
            Group.objects.get(id=self.group.id)


class TestConfirmAndDenyFacultyViews(TestCase):
    def setUp(self):
        self.school = SchoolFactory()
        self.icap = ICAPProfileFactory().user
        self.teacher = TeacherProfileFactory().user
        self.pending = StudentProfileFactory().user

        PendingTeachers.objects.create(user_profile=self.pending.profile,
                                       school=self.school)

        self.client = Client()

    def test_unauthorized(self):
        self.client.login(username=self.teacher.username, password="test")
        response = self.client.post('/faculty/confirm/',
                                    {'user_id': self.pending.id},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)

        response = self.client.post('/faculty/deny/',
                                    {'user_id': self.pending.id},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 403)

    def test_confirm_faculty(self):
        self.client.login(username=self.icap.username, password="test")
        response = self.client.post('/faculty/confirm/',
                                    {'user_id': self.pending.id},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.pending = User.objects.get(username=self.pending.username)
        self.assertTrue(self.pending.profile.is_teacher())
        self.assertEqual(self.pending.profile.school, self.school)
        self.assertEqual(self.pending.profile.country, self.school.country)

        self.assertEqual(PendingTeachers.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 1)

    def test_deny_faculty(self):
        self.client.login(username=self.icap.username, password="test")

        response = self.client.post('/faculty/deny/',
                                    {'user_id': self.pending.id},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.pending = User.objects.get(username=self.pending.username)
        self.assertTrue(self.pending.profile.is_student())

        self.assertEqual(PendingTeachers.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 1)


class TestCreateGroupView(TestCase):
    def setUp(self):
        self.teacher = TeacherProfileFactory().user
        self.school = SchoolFactory()
        self.client = Client()

        ModuleFactory("optionb-en", "/pages/optionb/en/")
        self.hierarchy = Hierarchy.objects.get(name='optionb-en')

    def test_student_forbidden(self):
        student = StudentProfileFactory().user
        self.client.login(username=student.username, password="test")
        response = self.client.get('/create_group/')
        self.assertEqual(response.status_code, 403)

    def test_create_group(self):
        self.client.login(username=self.teacher.username, password="test")

        data = {
            'start_date': '09/20/2018',
            'end_date': '09/29/2018',
            'name': 'The Group',
            'module': 'optionb-en'
        }

        response = self.client.post("/create_group/", data, follow=True)
        self.assertEqual(response.redirect_chain, [(
            '/dashboard/#user-groups', 302)])
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')

        group = Group.objects.get(name='The Group')
        self.assertEqual(group.formatted_start_date(), '09/20/2018')
        self.assertEqual(group.formatted_end_date(), '09/29/2018')
        self.assertEqual(group.module, self.hierarchy)


class TestPeopleViews(TestCase):

    def setUp(self):
        self.country = CountryFactory()
        self.school = SchoolFactory(country=self.country)
        self.affiliated_student = StudentProfileFactory(country=self.country)
        self.affiliated_teacher = TeacherProfileFactory(school=self.school,
                                                        country=self.country)
        self.random_student = StudentProfileFactory()
        self.icap = ICAPProfileFactory(school=self.school,
                                       country=self.country)

        self.client = Client()
        self.client.login(username=self.icap.user.username, password="test")

    def test_people_view(self):
        request = RequestFactory().get('/dashboard/people/')
        request.user = self.icap.user

        view = PeopleView()
        view.request = request

        ctx = view.get_context_data()
        self.assertTrue('countries' in ctx)
        self.assertTrue('roles' in ctx)
        self.assertEqual(ctx['user'], self.icap.user)

    def test_serialize(self):
        request = RequestFactory().get('/dashboard/people/filter/')
        request.user = self.icap.user

        view = PeopleFilterView()
        view.request = request

        profiles = [self.affiliated_student, self.affiliated_teacher,
                    self.icap]
        the_json = view.serialize_participants(profiles)
        self.assertEqual(len(the_json), 3)

        # student with an associated country
        self.assertEqual(the_json[0]['last_name'],
                         self.affiliated_student.user.last_name)
        self.assertTrue('school' not in the_json)
        self.assertEqual(the_json[0]['country'],
                         self.affiliated_student.country.display_name)

        # teacher with an associated country + school
        self.assertEqual(the_json[1]['last_name'],
                         self.affiliated_teacher.user.last_name)
        self.assertEqual(the_json[1]['school'],
                         self.affiliated_teacher.school.name)
        self.assertEqual(the_json[1]['country'],
                         self.affiliated_teacher.country.display_name)

        # icap admin
        self.assertEqual(the_json[2]['last_name'],
                         self.icap.user.last_name)
        self.assertEqual(the_json[2]['school'],
                         self.icap.school.name)
        self.assertEqual(the_json[2]['country'],
                         self.icap.country.display_name)

    def test_filter_by_role(self):
        request = RequestFactory().get('/dashboard/people/filter/',
                                       {'role': 'ST'})
        request.user = self.icap.user

        view = PeopleFilterView()
        view.request = request

        results = view.filter()

        self.assertEqual(results.count(), 2)
        self.assertTrue(results.get(id=self.affiliated_student.id))
        self.assertTrue(results.get(id=self.random_student.id))

    def test_filter_by_country(self):
        request = RequestFactory().get('/dashboard/people/filter/',
                                       {'country': self.country.name})
        request.user = self.icap.user

        view = PeopleFilterView()
        view.request = request

        results = view.filter()

        self.assertEqual(results.count(), 3)
        self.assertTrue(results.get(id=self.affiliated_student.id))
        self.assertTrue(results.get(id=self.affiliated_teacher.id))
        self.assertTrue(results.get(id=self.icap.id))

    def test_filter_by_country_and_institution(self):
        request = RequestFactory().get('/dashboard/people/filter/',
                                       {'country': self.country.name,
                                        'school': self.school.id})
        request.user = self.icap.user

        view = PeopleFilterView()
        view.request = request

        results = view.filter()

        self.assertEqual(results.count(), 2)
        self.assertTrue(results.get(id=self.affiliated_teacher.id))
        self.assertTrue(results.get(id=self.icap.id))

    def test_filter_by_role_country_and_institution(self):
        request = RequestFactory().get('/dashboard/people/filter/',
                                       {'role': 'IC',
                                        'country': self.country.name,
                                        'school': self.school.id})
        request.user = self.icap.user

        view = PeopleFilterView()
        view.request = request

        results = view.filter()

        self.assertEqual(results.count(), 1)
        self.assertTrue(results.get(id=self.icap.id))

    def test_get(self):
        request = RequestFactory().get('/dashboard/people/filter/',
                                       {'role': 'IC',
                                        'country': self.country.name,
                                        'school': self.school.id})
        request.user = self.icap.user

        view = PeopleFilterView()
        view.request = request

        response = view.get()

        the_json = json.loads(response.content)
        self.assertEqual(the_json['offset'], 0)
        self.assertEqual(the_json['total'], 1)
        self.assertEqual(the_json['count'], 1)
        self.assertEqual(the_json['limit'], view.MAX_PEOPLE)
        self.assertEqual(len(the_json['participants']), 1)

    def test_forbidden(self):
        self.client.login(username=self.random_student.user.username,
                          password="test")
        response = self.client.get('/dashboard/people/')
        self.assertEqual(response.status_code, 403)
        response = self.client.get('/dashboard/people/filter/')
        self.assertEqual(response.status_code, 403)

        self.client.login(username=self.affiliated_teacher.user.username,
                          password="test")
        response = self.client.get('/dashboard/people/')
        self.assertEqual(response.status_code, 403)
        response = self.client.get('/dashboard/people/filter/')
        self.assertEqual(response.status_code, 403)

        country_admin = CountryAdministratorProfileFactory()
        self.client.login(username=country_admin.user.username,
                          password="test")
        response = self.client.get('/dashboard/people/')
        self.assertEqual(response.status_code, 403)
        response = self.client.get('/dashboard/people/filter/')
        self.assertEqual(response.status_code, 403)


class TestDetailViews(TestCase):
    def setUp(self):
        ModuleFactory("optionb-en", "/pages/optionb/en/")
        hierarchy = Hierarchy.objects.get(name='optionb-en')

        self.group = SchoolGroupFactory(module=hierarchy)
        country = self.group.school.country

        self.icap = ICAPProfileFactory(school=self.group.school,
                                       country=country).user

        self.student = StudentProfileFactory(country=country).user
        self.student.profile.group.add(self.group)
        self.student2 = StudentProfileFactory(country=country).user
        self.student2.profile.group.add(self.group)

    def test_student_access(self):
        self.client.login(username=self.student.username, password="test")
        args = [self.group.id]

        resp = self.client.get(reverse('group-details', args=args))
        self.assertEqual(resp.status_code, 403)

        resp = self.client.get(reverse('roster-details', args=args))
        self.assertEqual(resp.status_code, 403)

        args.append(self.student.id)
        resp = self.client.get(reverse('student-group-details', args=args))
        self.assertEqual(resp.status_code, 403)

    def test_icap_access(self):
        self.client.login(username=self.icap.username, password="test")
        args = [self.group.id]

        resp = self.client.get(reverse('group-details', args=args))
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get(reverse('roster-details', args=args))
        self.assertEqual(resp.status_code, 200)

        args.append(self.student.id)
        resp = self.client.get(reverse('student-group-details', args=args))
        self.assertEqual(resp.status_code, 200)

    def test_group_detail(self):
        url = reverse('group-details', args=[self.group.id])
        request = RequestFactory().get(url)
        request.user = self.icap

        view = GroupDetail()
        view.request = request
        view.object = self.group
        view.kwargs = {'pk': self.group.id}

        self.assertEqual(view.get_object(), self.group)

        ctx = view.get_context_data(**view.kwargs)
        self.assertEqual(ctx['group'], self.group)
        self.assertEqual(ctx['object'], self.group)
        self.assertEqual(len(ctx['stats']), 1)

        self.assertEqual(ctx['stats'][0]['completed'], 0)
        self.assertEqual(ctx['stats'][0]['inprogress'], 0)
        self.assertEqual(ctx['stats'][0]['incomplete'], 0)
        self.assertEqual(ctx['stats'][0]['total'], 2)
        self.assertEqual(ctx['stats'][0]['language'], 'English')

    def test_roster_detail(self):
        url = reverse('roster-details', args=[self.group.id])
        request = RequestFactory().get(url)
        request.user = self.icap

        view = RosterDetail()
        view.request = request
        view.object = self.group
        view.kwargs = {'pk': self.group.id}

        self.assertEqual(view.get_object(), self.group)

        ctx = view.get_context_data(**view.kwargs)
        self.assertEqual(ctx['group'], self.group)
        self.assertEqual(ctx['object'], self.group)

    def test_student_detail(self):
        url = reverse('student-group-details',
                      args=[self.group.id, self.student.id])
        request = RequestFactory().get(url)
        request.user = self.icap

        view = StudentGroupDetail()
        view.request = request
        view.object = self.group
        view.kwargs = {'group_id': self.group.id,
                       'student_id': self.student.id}

        ctx = view.get_context_data(**view.kwargs)
        self.assertEqual(ctx['group'], self.group)
        self.assertEqual(ctx['student'], self.student)
        self.assertIsNone(ctx['progress_report']['satisfaction'])
        self.assertIsNone(ctx['progress_report']['pretest'])
        self.assertIsNone(ctx['progress_report']['posttest'])
        self.assertEqual(ctx['progress_report']['total_users'], 1)
        self.assertEqual(ctx['progress_report']['sessions'],
                         [None, None, None])


class AddUserToGroupTest(TestCase):

    def setUp(self):
        ModuleFactory("optionb-en", "/pages/optionb/en/")
        hierarchy = Hierarchy.objects.get(name='optionb-en')

        self.group = SchoolGroupFactory(module=hierarchy)
        self.icap = ICAPProfileFactory(school=self.group.school,
                                       country=self.group.school.country).user

    def test_access(self):
        student = StudentProfileFactory(country=self.group.school.country).user
        data = {'group': self.group.id, 'usernames': student.username}

        # not logged in
        response = self.client.post(reverse('add-to-group'), data)
        self.assertEqual(response.status_code, 302)

        # not icap
        self.client.login(username=student.username, password="test")
        response = self.client.post(reverse('add-to-group'), data)
        self.assertEqual(response.status_code, 403)

    def test_add_one(self):
        student = StudentProfileFactory(country=self.group.school.country).user
        self.assertTrue(self.group not in student.profile.group.all())

        data = {'group': self.group.id,
                'usernames': student.username}

        self.client.login(username=self.icap.username, password="test")
        response = self.client.post(reverse('add-to-group'), data)
        self.assertEqual(response.status_code, 302)

        self.assertTrue(self.group in student.profile.group.all())

    def test_add_many(self):
        s1 = StudentProfileFactory(country=self.group.school.country).user
        s2 = StudentProfileFactory(country=self.group.school.country).user
        usernames = "%s\n%s\nfoobar" % (s1.username, s2.username)

        data = {'group': self.group.id, 'usernames': usernames}

        self.client.login(username=self.icap.username, password="test")
        response = self.client.post(reverse('add-to-group'), data)
        self.assertEqual(response.status_code, 302)

        self.assertTrue(self.group in s1.profile.group.all())
        self.assertTrue(self.group in s2.profile.group.all())
