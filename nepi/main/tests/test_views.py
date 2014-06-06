from django.test import TestCase, RequestFactory
from django.test.client import Client
from django.contrib.auth.models import User
from nepi.main.models import UserProfile, Country
from factories import UserFactory, HierarchyFactory, UserProfileFactory
from factories import CourseFactory

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

#     def test_home(self):
#         response = self.c.get("/", follow=True)
#         self.assertEqual(response.status_code, 200)
#         self.assertEquals(response.redirect_chain[0],
#                           ('http://testserver/accounts/login/?next=/',
#                            302))

    def test_about(self):
        response = self.c.get("/about/")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('flatpages/about.html')

    def test_help(self):
        response = self.c.get("/help/")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('flatpages/help.html')

#    def test_contact(self):
#        request = self.factory.post('/contact/',
#                                    {"subject": "new_student",
#                                     "message": "new_student",
#                                     "sender": "new_student",
#                                     "recipients": "email@email.com"})
#        response = contact(request)
#        self.assertEqual(response.status_code, 200)

    def test_smoketest(self):
        response = self.c.get("/smoketest/")
        self.assertEquals(response.status_code, 200)

    def test_register_form(self):
        r = self.c.get("/register/")
        self.assertEqual(r.status_code, 200)

    def test_register_form_invalid_submission(self):
        r = self.c.post("/register/", dict())
        self.assertEqual(r.status_code, 200)


class TestLoggedInViews(TestCase):
    def setUp(self):
        self.h = HierarchyFactory()
        self.s = self.h.get_root().get_first_leaf()
        self.u = UserFactory(is_superuser=True)
        self.up = UserProfileFactory(user=self.u)
        self.u.set_password("test")
        self.u.save()
        self.c = Client()
        self.c.login(username=self.u.username, password="test")

    def test_edit_page_form(self):
        r = self.c.get("/pages/%s/edit/%s/" % (self.h.name, self.s.slug))
        self.assertEqual(r.status_code, 200)

    def test_page(self):
        r = self.c.get("/pages/%s/%s/" % (self.h.name, self.s.slug))
        self.assertEqual(r.status_code, 200)

#    def test_home(self):
#        response = self.c.get("/")
#        # self.assertEqual(response.status_code, 200)
