from django.test import TestCase, RequestFactory
from django.test.client import Client
from django.contrib.auth.models import User
from nepi.main.models import UserProfile
from nepi.activities.models import ConversationScenario
from nepi.main.tests.factories import UserFactory, \
    HierarchyFactory, UserProfileFactory

'''make sure logged in super user can
create conversation scenario pageblocks'''


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
        self.factory = RequestFactory()

    def test_edit_conversation_page_form(self):
        r = self.c.get("/pages/%s/edit/%s/" % (self.h.name, self.s.slug))
        request = self.factory.post(
            "/pages/%s/edit/%s/" % (self.h.name, self.s.slug),
            {"lable": "conversation label",
             "description": "conversation description"})
        request.user = self.u
        conversation = ConversationScenario.create(request)
        conversation.save()
        self.assertEqual(r.status_code, 200)


#     def test_page(self):
#         r = self.c.get("/pages/%s/%s/" % (self.h.name, self.s.slug))
#         self.assertEqual(r.status_code, 200)
#
#     def test_home(self):
#         response = self.c.get("/")
#         self.assertEqual(response.status_code, 200)
