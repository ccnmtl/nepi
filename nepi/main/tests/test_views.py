from django.test import TestCase, RequestFactory
from django.test.client import Client
from django.contrib.auth.models import User
from nepi.main.views import register, contact
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
                                    {   "subject": "new_student",
                                        "message": "new_student",
                                        "sender": "new_student",
                                        "recipients": "email@email.com"})
        response = contact(request)
        self.assertEqual(response.status_code, 200)

    # Now create account and login - will default to student
    # def test_registration_and_login(self):
    #     request = self.factory.post('/register/',
    #                                 {"username": "new_student",
    #                                     "password1": "new_student",
    #                                     "password2": "new_student",
    #                                     "email": "email@email.com",
    #                                     "first_name": "new_student",
    #                                     "last_name": "new_student",
    #                                     "country": "DZ",
    #                                     # "profile_type": "ST",
    #                                     "is_teacher": "ST"})
    #     response = register(request)
    #     self.assertEqual(response.status_code, 302)


    # def test_client_registration_and_login(self):
    #     request = self.c.post('/register/',
    #                           {"username": "new_person",
    #                            "password1": "new_student",
    #                            "password2": "new_student",
    #                            "email": "email@email.com",
    #                            "first_name": "new_student",
    #                            "last_name": "new_student",
    #                            "country": "DZ",
    #                            # "profile_type": "ST",
    #                            "is_teacher": "ST"})
    #     redirect = "/thank_you_reg/"
    #     self.assertRedirects(request, redirect)
    #     self.assertTemplateUsed('flatpages/thanks.html')

    #     request = self.c.post('/login/',
    #                           {"username": "new_person",
    #                            "password": "new_student"})
    #     redirect = "/home/"
    #     self.assertRedirects(request, redirect)
    #     self.assertTemplateUsed('flatpages/stindex.html')


    def test_smoketest(self):
        response = self.c.get("/smoketest/")
        self.assertEquals(response.status_code, 200)
        assert "PASS" in response.content


    # # # Test ICAP User Experience
    # def test_icap_login_and_links(self):
    #     """Make sure ICAP personel can log in and visit
    #     all of the links for the functionality they have."""
    #     request = self.c.post('/login/',
    #                           {"username": "icap_user",
    #                            "password": "icap_user"})
    #     redirect = "/home/"
    #     self.assertRedirects(request, redirect)
    #     self.assertTemplateUsed('icap/icindex.html')
        # request = self.c.post('/add_school/',
        #                       {"country": "NG",
        #                        "name": "new_school"})
        # redirect = "/thank_you_school/"
        # self.assertRedirects(request, redirect)

    # def test_teacher_account(self):
    #     pass

    # def test_student_account(self):
    #     pass
