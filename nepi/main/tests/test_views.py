from django.test import TestCase, RequestFactory
from django.test.client import Client
from django.contrib.auth.models import User
from nepi.main.views import contact
from nepi.main.models import UserProfile, Country


class TestBasicViews(TestCase):

    def setUp(self):
        self.c = Client()
        self.factory = RequestFactory()
        # ICAP User
        self.icap_user = User.objects.create_user(
            'icap_user', 'icap@icap.com', 'icap_user')
        self.icap_user.save()
        self.country = Country(name='AO', region="region")
        self.country.save()
        self.user_profile = UserProfile(
            user=self.icap_user, profile_type='IC', country=self.country)
        self.user_profile.save()

    def test_root(self):
        response = self.c.get("/")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('flatpages/index.html')

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
        response = contact(request)
        self.assertEqual(response.status_code, 200)

    def test_smoketest(self):
        response = self.c.get("/smoketest/")
        self.assertEquals(response.status_code, 200)
        assert "PASS" in response.content
