from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.test.client import Client
from factories import UserFactory, HierarchyFactory, UserProfileFactory, \
    TeacherProfileFactory, ICAPProfileFactory
from nepi.main.models import UserProfile, Country
from nepi.main.views import ContactView, ViewPage
from pagetree.models import UserPageVisit, Section


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
                                     "sender": "new_student",
                                     "recipients": "email@email.com"})
        response = ContactView.as_view()(request)
        self.assertEqual(response.status_code, 200)

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
