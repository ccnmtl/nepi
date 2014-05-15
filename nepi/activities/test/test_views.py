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
        self.hierarchy = HierarchyFactory()
        self.section = self.hierarchy.get_root().get_first_leaf()
        self.user = UserFactory(is_superuser=True)
        self.up = UserProfileFactory(user=self.user)
        self.user.set_password("test")
        self.user.save()
        self.client = Client()
        self.client.login(username=self.user.username, password="test")
        self.factory = RequestFactory()

    def test_edit_conversation_page_form(self):
        r = self.client.get("/pages/%s/edit/%s/" %
                            (self.hierarchy.name, self.section.slug))
        request = self.factory.post(
            "/pages/%s/edit/%s/" % (self.hierarchy.name, self.section.slug),
            {"label": "conversation label",
             "description": "conversation description"})
        request.user = self.user
        conversation = ConversationScenario.create(request)
        self.assertTrue(conversation.needs_submit())
        self.assertFalse(conversation.unlocked(request.user))
        self.assertEqual(r.status_code, 200)


#     def test_page(self):
#         r = self.c.get("/pages/%s/%s/" % (self.h.name, self.s.slug))
#         self.assertEqual(r.status_code, 200)
#
#     def test_home(self):
#         response = self.c.get("/")
#         self.assertEqual(response.status_code, 200)
