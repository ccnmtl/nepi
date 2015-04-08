from datetime import datetime
import json

from django.contrib.auth.models import User
from django.core import mail
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory
from django.test.client import Client
from pagetree.models import UserPageVisit, Section, Hierarchy
from pagetree.tests.factories import ModuleFactory

from factories import UserFactory, UserProfileFactory, TeacherProfileFactory, \
    ICAPProfileFactory
from nepi.main.forms import ContactForm
from nepi.main.models import Country, School, Group, PendingTeachers
from nepi.main.tests.factories import SchoolFactory, CountryFactory, \
    SchoolGroupFactory, StudentProfileFactory, \
    CountryAdministratorProfileFactory, \
    InstitutionAdminProfileFactory, PendingTeacherFactory
from nepi.main.views import ContactView, ViewPage, CreateSchoolView, \
    UserProfileView, PeopleView, PeopleFilterView, RosterDetail, GroupDetail, \
    StudentGroupDetail


class TestBasicViews(TestCase):

    def test_home(self):
        response = self.client.get("/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.redirect_chain[0],
                          ('http://testserver/accounts/login/?next=/', 302))

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
        self.client.login(username=self.student.username, password="test")

    def test_edit_page_form(self):
        response = self.client.get(self.section.get_edit_url())
        self.assertEqual(response.status_code, 302)

    def test_page(self):
        response = self.client.get(self.section.get_absolute_url(),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/pages/main/one/', 302)])

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
        self.assertEquals(ctx['countries'], Country.choices())
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
        response = self.client.get(self.section.get_absolute_url(),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/pages/main/one/', 302)])

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

        self.assertEquals(view.get_object(), request.user.profile)

        view.object = request.user.profile
        ctx = view.get_context_data()

        self.assertEquals(ctx['optionb'], self.hierarchy)
        self.assertIsNotNone(ctx['profile_form'])
        self.assertEquals(ctx['countries'], Country.choices())
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
        response = self.client.get(self.section.get_absolute_url(),
                                   follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/pages/main/one/', 302)])

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

        self.assertEquals(view.get_object(), request.user.profile)

        view.object = request.user.profile
        ctx = view.get_context_data()

        self.assertEquals(ctx['optionb'], self.hierarchy)
        self.assertIsNotNone(ctx['profile_form'])
        self.assertEquals(ctx['countries'], Country.choices())
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
        response = self.client.get(self.section.get_absolute_url(),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/pages/main/one/', 302)])

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

        self.assertEquals(view.get_object(), request.user.profile)

        view.object = request.user.profile
        ctx = view.get_context_data()

        self.assertEquals(ctx['optionb'], self.hierarchy)
        self.assertIsNotNone(ctx['profile_form'])
        self.assertEquals(ctx['countries'], Country.choices())
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
        response = self.client.get(self.section.get_absolute_url(),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/pages/main/one/', 302)])

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

        a = SchoolGroupFactory()
        b = SchoolGroupFactory()
        SchoolGroupFactory(archived=True)

        view = UserProfileView()
        view.request = request

        self.assertEquals(view.get_object(), request.user.profile)

        view.object = request.user.profile
        ctx = view.get_context_data()

        self.assertEquals(ctx['optionb'], self.hierarchy)
        self.assertIsNotNone(ctx['profile_form'])
        self.assertEquals(ctx['countries'], Country.choices())
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
        cache.clear()
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
        self.assertEquals(len(the_json['schools']), 0)

    def test_get_schools(self):
        response = self.client.get('/schools/%s/' % self.school.country.name,
                                   {},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEquals(len(the_json['schools']), 1)

        self.assertEquals(the_json['schools'][0]['id'], str(self.school.id))
        self.assertEquals(the_json['schools'][0]['name'], self.school.name)


class TestSchoolGroupChoiceView(TestCase):

    def setUp(self):
        self.user = TeacherProfileFactory().user
        self.client = Client()
        self.client.login(username=self.user.username, password="test")

    def test_ajax_only(self):
        grp = SchoolGroupFactory()
        response = self.client.post('/groups/%s/' % grp.school.id)
        self.assertEquals(response.status_code, 405)

    def test_get_school_not_found(self):
        response = self.client.post('/groups/782/', {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 404)

    def test_get_no_groups(self):
        school = SchoolFactory()
        response = self.client.post('/groups/%s/' % school.id,
                                    {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEquals(len(the_json['groups']), 0)

    def test_get_groups(self):
        grp = SchoolGroupFactory()

        response = self.client.post('/groups/%s/' % grp.school.id,
                                    {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEquals(len(the_json['groups']), 1)

        self.assertEquals(the_json['groups'][0]['id'], str(grp.id))
        self.assertEquals(the_json['groups'][0]['name'], grp.name)

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
        self.assertEquals(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEquals(len(the_json['groups']), 1)

        self.assertEquals(the_json['groups'][0]['id'], str(grp.id))
        self.assertEquals(the_json['groups'][0]['name'], grp.name)

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
        self.assertEquals(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEquals(len(the_json['groups']), 1)

        self.assertEquals(the_json['groups'][0]['id'], str(created.id))
        self.assertEquals(the_json['groups'][0]['name'], created.name)


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
        self.assertEquals(ctx['user'], self.icap.user)

    def test_serialize(self):
        request = RequestFactory().get('/dashboard/people/filter/')
        request.user = self.icap.user

        view = PeopleFilterView()
        view.request = request

        profiles = [self.affiliated_student, self.affiliated_teacher,
                    self.icap]
        the_json = view.serialize_participants(profiles)
        self.assertEquals(len(the_json), 3)

        # student with an associated country
        self.assertEquals(the_json[0]['last_name'],
                          self.affiliated_student.user.last_name)
        self.assertTrue('school' not in the_json)
        self.assertEquals(the_json[0]['country'],
                          self.affiliated_student.country.display_name)

        # teacher with an associated country + school
        self.assertEquals(the_json[1]['last_name'],
                          self.affiliated_teacher.user.last_name)
        self.assertEquals(the_json[1]['school'],
                          self.affiliated_teacher.school.name)
        self.assertEquals(the_json[1]['country'],
                          self.affiliated_teacher.country.display_name)

        # icap admin
        self.assertEquals(the_json[2]['last_name'],
                          self.icap.user.last_name)
        self.assertEquals(the_json[2]['school'],
                          self.icap.school.name)
        self.assertEquals(the_json[2]['country'],
                          self.icap.country.display_name)

    def test_filter_by_role(self):
        request = RequestFactory().get('/dashboard/people/filter/',
                                       {'role': 'ST'})
        request.user = self.icap.user

        view = PeopleFilterView()
        view.request = request

        results = view.filter()

        self.assertEquals(results.count(), 2)
        self.assertTrue(results.get(id=self.affiliated_student.id))
        self.assertTrue(results.get(id=self.random_student.id))

    def test_filter_by_country(self):
        request = RequestFactory().get('/dashboard/people/filter/',
                                       {'country': self.country.name})
        request.user = self.icap.user

        view = PeopleFilterView()
        view.request = request

        results = view.filter()

        self.assertEquals(results.count(), 3)
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

        self.assertEquals(results.count(), 2)
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

        self.assertEquals(results.count(), 1)
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
        self.assertEquals(the_json['offset'], 0)
        self.assertEquals(the_json['total'], 1)
        self.assertEquals(the_json['count'], 1)
        self.assertEquals(the_json['limit'], view.MAX_PEOPLE)
        self.assertEquals(len(the_json['participants']), 1)

    def test_forbidden(self):
        self.client.login(username=self.random_student.user.username,
                          password="test")
        response = self.client.get('/dashboard/people/')
        self.assertEquals(response.status_code, 403)
        response = self.client.get('/dashboard/people/filter/')
        self.assertEquals(response.status_code, 403)

        self.client.login(username=self.affiliated_teacher.user.username,
                          password="test")
        response = self.client.get('/dashboard/people/')
        self.assertEquals(response.status_code, 403)
        response = self.client.get('/dashboard/people/filter/')
        self.assertEquals(response.status_code, 403)

        country_admin = CountryAdministratorProfileFactory()
        self.client.login(username=country_admin.user.username,
                          password="test")
        response = self.client.get('/dashboard/people/')
        self.assertEquals(response.status_code, 403)
        response = self.client.get('/dashboard/people/filter/')
        self.assertEquals(response.status_code, 403)


class TestDetailViews(TestCase):
    def setUp(self):
        ModuleFactory("main", "/pages/main/")
        hierarchy = Hierarchy.objects.get(name='main')

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
        self.assertEquals(resp.status_code, 403)

        resp = self.client.get(reverse('roster-details', args=args))
        self.assertEquals(resp.status_code, 403)

        args.append(self.student.id)
        resp = self.client.get(reverse('student-group-details', args=args))
        self.assertEquals(resp.status_code, 403)

    def test_icap_access(self):
        self.client.login(username=self.icap.username, password="test")
        args = [self.group.id]

        resp = self.client.get(reverse('group-details', args=args))
        self.assertEquals(resp.status_code, 200)
        resp = self.client.get(reverse('roster-details', args=args))
        self.assertEquals(resp.status_code, 200)

        args.append(self.student.id)
        resp = self.client.get(reverse('student-group-details', args=args))
        self.assertEquals(resp.status_code, 200)

    def test_group_detail(self):
        url = reverse('group-details', args=[self.group.id])
        request = RequestFactory().get(url)
        request.user = self.icap

        view = GroupDetail()
        view.request = request
        view.object = self.group
        view.kwargs = {'pk': self.group.id}

        self.assertEquals(view.get_object(), self.group)

        ctx = view.get_context_data(**view.kwargs)
        self.assertEquals(ctx['group'], self.group)
        self.assertEquals(ctx['object'], self.group)
        self.assertEquals(len(ctx['completed_users']), 0)
        self.assertEquals(ctx['completed'], 0)
        self.assertEquals(ctx['inprogress'], 0)
        self.assertEquals(ctx['incomplete'], 0)
        self.assertEquals(ctx['total'], 2)

    def test_roster_detail(self):
        url = reverse('roster-details', args=[self.group.id])
        request = RequestFactory().get(url)
        request.user = self.icap

        view = RosterDetail()
        view.request = request
        view.object = self.group
        view.kwargs = {'pk': self.group.id}

        self.assertEquals(view.get_object(), self.group)

        ctx = view.get_context_data(**view.kwargs)
        self.assertEquals(ctx['group'], self.group)
        self.assertEquals(ctx['object'], self.group)

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
        self.assertEquals(ctx['group'], self.group)
        self.assertEquals(ctx['student'], self.student)
        self.assertIsNone(ctx['progress_report']['satisfaction'])
        self.assertIsNone(ctx['progress_report']['pretest'])
        self.assertIsNone(ctx['progress_report']['posttest'])
        self.assertEquals(ctx['progress_report']['total_users'], 1)
        self.assertEquals(ctx['progress_report']['sessions'],
                          [None, None, None])
