'''Creating test just for registration since it is prone to changing'''
from django.test import TestCase, RequestFactory
from nepi.main.models import Country, School
from nepi.main.models import PendingTeachers
from nepi.main.views import RegistrationView
from django.test.client import Client
from factories import GroupFactory, UserProfileFactory

class TestRegistration(TestCase):
    def setUp(self):
        self.c = Client()
        self.factory = RequestFactory()
        self.country = Country(name='LS')
        self.country.save()
        self.school = School(country=self.country, name='School 1')
        self.school.save()
        self.group = GroupFactory()


    def test_student_cbv_reg(self):
        #hierarcy = HierarchyFactory()
        #new_user = UserProfileFactory()
        request = self.factory.post(
            "/register/",
            {"first_name": "regstudent", "last_name": "regstudent",
             "username": "regstudent", "email": "test_email@email.com",
             "password1": "regstudent", "password2": "regstudent",
             "country": "LS", "profile_type": False,
             "captcha": True})
        request.user = self.user
        response = RegistrationView.as_view()(request)
#         #response = ConversationResponse.objects.create(request)
#         self.assertEqual(response.status_code, 200)
#         #self.assertTrue(response.needs_submit())
#         #self.assertFalse(response.unlocked(request.user))

    def test_student_registration_and_login(self):
        '''when students are registered they should not be added to pending'''
        response = self.c.post(
            '/register/',
            {"first_name": "regstudent", "last_name": "regstudent",
             "username": "regstudent", "email": "test_email@email.com",
             "password1": "regstudent", "password2": "regstudent",
             "country": "LS", "profile_type": False,
             "captcha": True}, follow=True)
        self.assertEquals(response.status_code, 200)
        self.pending = PendingTeachers.objects.all()
        self.assertFalse(self.pending.count())
        #self.assertEquals(response.redirect_chain,
        #                  ('http://testserver/thank_you_reg/',
        #                   302))
        #self.assertTemplateUsed('flatpages/help.html')
        #self.assertTrue()/thank_you_reg/
        #RegistrationView.as_view()(request)

    def test_teacher_registration_and_login(self):
        '''when teachers register they should
        be added to the pending teachers table'''
        response = self.c.post(
            '/register/',
            {"first_name": "reg_teacher", "last_name": "reg_teacher",
             "username": "reg_teacher", "email": "test_email@email.com",
             "password1": "reg_teacher", "password2": "reg_teacher",
             "country": "LS", "profile_type": True,
             "captcha": True}, follow=True)
        self.assertEquals(response.status_code, 200)
        # self.pending = PendingTeachers.objects.all()
        # self.assertTrue(self.pending.count())
        # I don't remember why I put this here
        # RegistrationView.as_view()(request)
        # new_teacher = User.objects.get(first_name="firstname")
        # self.assertTrue(new_teacher)
