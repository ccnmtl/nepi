from django.test import TestCase, RequestFactory
from django.test.client import Client
from django.contrib.auth.models import User
from nepi.main.views import index, about, help_page
from nepi.main.views import thank_you_reg, table_register


class TestBasicViews(TestCase):
    def setUp(self):
        self.c = Client()
        self.factory = RequestFactory()

    def test_root(self):
        response = self.c.get("/")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('main/index.html')

    def test_about(self):
        response = self.c.get("/about/")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('main/about.html')

    def test_help(self):
        response = self.c.get("/help_page/")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed('main/help.html')

    # Now create account and login - will default to student
    def test_registration_and_login(self):
        request = self.factory.post('/table_register/',
                                    {"username": "new_student",
                                        "password1": "new_student",
                                        "password2": "new_student",
                                        "email": "email@email.com",
                                        "first_name": "new_student",
                                        "last_name": "new_student",
                                        "country": "DZ",
                                        "profile_type": "ST",
                                        "is_teacher": "ST"})
        response = table_register(request)
        self.assertEqual(response.status_code, 302)

    def test_client_registration_and_login(self):
        request = self.c.post('/table_register/',
                              {"username": "new_person",
                               "password1": "new_student",
                               "password2": "new_student",
                               "email": "email@email.com",
                               "first_name": "new_student",
                               "last_name": "new_student",
                               "country": "DZ",
                               "profile_type": "ST",
                               "is_teacher": "ST"})
        redirect = "/thank_you_reg/"
        self.assertRedirects(request, redirect)
        self.assertTemplateUsed('main/thanks.html')

    # def test_thank_you_for_reg(self):
    #     response = self.c.get("/thank_you_reg//")
    #     self.assertEquals(response.status_code, 200)
    #     self.assertTemplateUsed('main/thanks.html')

    def test_smoketest(self):
        response = self.c.get("/smoketest/")
        self.assertEquals(response.status_code, 200)
        assert "PASS" in response.content
