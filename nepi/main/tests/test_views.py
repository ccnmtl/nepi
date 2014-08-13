from datetime import datetime
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, RequestFactory
from django.test.client import Client
from factories import UserFactory, UserProfileFactory, TeacherProfileFactory, \
    ICAPProfileFactory
from nepi.main.choices import COUNTRY_CHOICES
from nepi.main.forms import ContactForm
from nepi.main.models import Country, School, Group, PendingTeachers
from nepi.main.tests.factories import SchoolFactory, CountryFactory, \
    SchoolGroupFactory, StudentProfileFactory, \
    CountryAdministratorProfileFactory, \
    InstitutionAdminProfileFactory, PendingTeacherFactory
from nepi.main.views import ContactView, ViewPage, CreateSchoolView, \
    UserProfileView
from pagetree.models import UserPageVisit, Section, Hierarchy
from pagetree.tests.factories import ModuleFactory
import json


class TestBasicViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_home(self):
        response = self.client.get("/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.redirect_chain[0],
                          ('http://testserver/accounts/login/?next=/', 302))

    def test_about(self):
        response = self.client.get("/about/")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('flatpages/about.html')

    def test_help(self):
        response = self.client.get("/help/")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('flatpages/help.html')

    def test_contact(self):
        response = self.client.post('/contact/',
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
        ContactView().form_valid(form)
        self.assertEqual(len(mail.outbox), 1)

    def test_smoketest(self):
        response = self.client.get("/smoketest/")
        self.assertEquals(response.status_code, 200)


class TestStudentLoggedInViews(TestCase):
    '''go through some of the views student sees'''
    def setUp(self):
        ModuleFactory("main", "/pages/main/")
        self.hierarchy = Hierarchy.objects.get(name='main')
        self.section = self.hierarchy.get_root().get_first_leaf()

        self.student = StudentProfileFactory().user
        self.client = Client()
        self.client.login(username=self.student.username, password="test")

    def test_edit_page_form(self):
        response = self.client.get(self.section.get_edit_url())
        self.assertEqual(response.status_code, 302)

    def test_page(self):
        response = self.client.get(self.section.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_home(self):
        response = self.client.get("/", follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/dashboard/#user-modules', 302)])
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')

    def test_home_noprofile(self):
        user = UserFactory()
        self.client.login(username=user.username, password="test")

        response = self.client.get("/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.redirect_chain[0],
                          ('http://testserver/register/', 302))

    def test_dashboard(self):
        response = self.client.get('/dashboard/')
        self.assertEquals(response.status_code, 200)

    def test_dashboard_context(self):
        request = RequestFactory().get('/dashboard/')
        request.user = self.student

        view = UserProfileView()
        view.request = request

        self.assertEquals(view.get_object(), request.user.profile)

        view.object = request.user.profile
        ctx = view.get_context_data()

        self.assertEquals(ctx['optionb'], self.hierarchy)
        self.assertIsNotNone(ctx['profile_form'])
        self.assertEquals(ctx['countries'], COUNTRY_CHOICES)
        self.assertEquals(ctx['joined_groups'].count(), 0)
        self.assertTrue('managed_groups' not in ctx)
        self.assertTrue('pending_teachers' not in ctx)


class TestTeacherLoggedInViews(TestCase):

    def setUp(self):
        ModuleFactory("main", "/pages/main/")
        self.hierarchy = Hierarchy.objects.get(name='main')
        self.section = self.hierarchy.get_root().get_first_leaf()

        self.teacher = TeacherProfileFactory().user
        self.client = Client()
        self.client.login(username=self.teacher.username, password="test")

    def test_page(self):
        response = self.client.get(self.section.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_home(self):
        response = self.client.get("/", follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/dashboard/#user-groups', 302)])
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')

    def test_dashboard(self):
        response = self.client.get('/dashboard/')
        self.assertEquals(response.status_code, 200)

    def test_dashboard_context(self):
        request = RequestFactory().get('/dashboard/')
        request.user = self.teacher

        view = UserProfileView()
        view.request = request

        self.assertEquals(view.get_object(), request.user.profile)

        view.object = request.user.profile
        ctx = view.get_context_data()

        school_group = SchoolGroupFactory(creator=self.teacher,
                                          school=self.teacher.profile.school)

        # archived group
        SchoolGroupFactory(creator=self.teacher,
                           school=self.teacher.profile.school,
                           archived=True)
        # alt_creator
        SchoolGroupFactory(creator=TeacherProfileFactory().user)

        self.assertEquals(ctx['optionb'], self.hierarchy)
        self.assertIsNotNone(ctx['profile_form'])
        self.assertEquals(ctx['countries'], COUNTRY_CHOICES)
        self.assertEquals(ctx['joined_groups'].count(), 0)
        self.assertEquals(len(ctx['managed_groups']), 1)
        self.assertEquals(ctx['managed_groups'][0], school_group)
        self.assertTrue('pending_teachers' not in ctx)


class TestInstitutionAdminLoggedInViews(TestCase):

    def setUp(self):
        ModuleFactory("main", "/pages/main/")
        self.hierarchy = Hierarchy.objects.get(name='main')
        self.section = self.hierarchy.get_root().get_first_leaf()

        self.admin = InstitutionAdminProfileFactory().user
        self.client = Client()
        self.client.login(username=self.admin.username, password="test")

        self.teacher = TeacherProfileFactory(
            school=self.admin.profile.school).user

    def test_page(self):
        response = self.client.get(self.section.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_home(self):
        response = self.client.get("/", follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/dashboard/#user-groups', 302)])
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')

    def test_dashboard(self):
        response = self.client.get('/dashboard/')
        self.assertEquals(response.status_code, 200)

    def test_dashboard_context(self):
        request = RequestFactory().get('/dashboard/')
        request.user = self.admin

        view = UserProfileView()
        view.request = request

        self.assertEquals(view.get_object(), request.user.profile)

        view.object = request.user.profile
        ctx = view.get_context_data()

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

        self.assertEquals(ctx['optionb'], self.hierarchy)
        self.assertIsNotNone(ctx['profile_form'])
        self.assertEquals(ctx['countries'], COUNTRY_CHOICES)
        self.assertEquals(ctx['joined_groups'].count(), 0)
        self.assertEquals(len(ctx['managed_groups']), 2)
        self.assertEquals(ctx['managed_groups'][0], admin_group)
        self.assertEquals(ctx['managed_groups'][1], teacher_group)

        # pending teachers
        PendingTeacherFactory()  # random country/school
        alt_school = SchoolFactory(country=self.admin.profile.country)
        PendingTeacherFactory(school=alt_school)  # same country, diff school
        pt = PendingTeacherFactory(school=self.admin.profile.school)  # visible
        self.assertEquals(len(ctx['pending_teachers']), 1)
        self.assertEquals(ctx['pending_teachers'][0], pt)


class TestCountryAdminLoggedInViews(TestCase):

    def setUp(self):
        ModuleFactory("main", "/pages/main/")
        self.hierarchy = Hierarchy.objects.get(name='main')
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
        response = self.client.get(self.section.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_home(self):
        response = self.client.get("/", follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/dashboard/#user-groups', 302)])
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')

    def test_dashboard(self):
        response = self.client.get('/dashboard/')
        self.assertEquals(response.status_code, 200)

    def test_dashboard_context(self):
        request = RequestFactory().get('/dashboard/')
        request.user = self.admin

        view = UserProfileView()
        view.request = request

        self.assertEquals(view.get_object(), request.user.profile)

        view.object = request.user.profile
        ctx = view.get_context_data()

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

        self.assertEquals(ctx['optionb'], self.hierarchy)
        self.assertIsNotNone(ctx['profile_form'])
        self.assertEquals(ctx['countries'], COUNTRY_CHOICES)
        self.assertEquals(ctx['joined_groups'].count(), 0)
        self.assertEquals(len(ctx['managed_groups']), 3)
        self.assertEquals(ctx['managed_groups'][0], admin_group)
        self.assertEquals(ctx['managed_groups'][1], teacher_group)
        self.assertEquals(ctx['managed_groups'][2], iadmin_group)

        # pending teachers
        PendingTeacherFactory()  # random country/school
        pt1 = PendingTeacherFactory(school=self.alt_school)
        pt2 = PendingTeacherFactory(school=self.school)  # visible
        self.assertEquals(len(ctx['pending_teachers']), 2)
        self.assertEquals(ctx['pending_teachers'][0], pt2)
        self.assertEquals(ctx['pending_teachers'][1], pt1)


class TestICAPLoggedInViews(TestCase):

    def setUp(self):
        ModuleFactory("main", "/pages/main/")
        self.hierarchy = Hierarchy.objects.get(name='main')
        self.section = self.hierarchy.get_root().get_first_leaf()

        self.icap = ICAPProfileFactory().user
        self.client = Client()
        self.client.login(username=self.icap.username, password="test")

    def test_page(self):
        response = self.client.get(self.section.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_home(self):
        response = self.client.get("/", follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/dashboard/#user-groups', 302)])
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')

    def test_dashboard(self):
        response = self.client.get('/dashboard/')
        self.assertEquals(response.status_code, 200)

    def test_dashboard_context(self):
        request = RequestFactory().get('/dashboard/')
        request.user = self.icap

        view = UserProfileView()
        view.request = request

        self.assertEquals(view.get_object(), request.user.profile)

        view.object = request.user.profile
        ctx = view.get_context_data()

        a = SchoolGroupFactory()
        b = SchoolGroupFactory()
        SchoolGroupFactory(archived=True)

        self.assertEquals(ctx['optionb'], self.hierarchy)
        self.assertIsNotNone(ctx['profile_form'])
        self.assertEquals(ctx['countries'], COUNTRY_CHOICES)
        self.assertEquals(ctx['joined_groups'].count(), 0)
        self.assertEquals(len(ctx['managed_groups']), 2)
        self.assertEquals(ctx['managed_groups'][0], a)
        self.assertEquals(ctx['managed_groups'][1], b)

        # pending teachers
        pt = PendingTeacherFactory()  # random country/school
        self.assertEquals(len(ctx['pending_teachers']), 1)
        self.assertEquals(ctx['pending_teachers'][0], pt)


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


class TestCreateGroupView(TestCase):
    def setUp(self):
        self.teacher = TeacherProfileFactory().user
        self.school = SchoolFactory()
        self.client = Client()

        ModuleFactory("main", "/pages/main/")
        self.hierarchy = Hierarchy.objects.get(name='main')

    def test_student_forbidden(self):
        student = StudentProfileFactory().user
        self.client.login(username=student.username, password="test")
        response = self.client.get('/create_group/')
        self.assertEquals(response.status_code, 403)

    def test_create_group(self):
        self.client.login(username=self.teacher.username, password="test")

        data = {
            'start_date': '09/20/2018',
            'end_date': '09/29/2018',
            'name': 'The Group',
            'module': 'main'
        }

        response = self.client.post("/create_group/", data, follow=True)
        self.assertEquals(response.redirect_chain, [(
            'http://testserver/dashboard/#user-groups', 302)])
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')

        group = Group.objects.get(name='The Group')
        self.assertEquals(group.formatted_start_date(), '09/20/2018')
        self.assertEquals(group.formatted_end_date(), '09/29/2018')
        self.assertEquals(group.module, self.hierarchy)
