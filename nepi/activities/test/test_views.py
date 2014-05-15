from django.test import TestCase, RequestFactory
from django.test.client import Client
from nepi.activities.models import ConversationScenario
from nepi.main.tests.factories import UserFactory, \
    HierarchyFactory, UserProfileFactory

'''make sure logged in super user can
create conversation scenario pageblocks'''


class TestLoggedInViews(TestCase):
    '''Going through scenario of admin goes to admin panel:
        1. admin creates conversation pageblock.
        2. admin then decides to update the conversation information
        3. admin then adds conversations to the conversation scenario
        4. admin then edits the conversations
    '''
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
        self.assertEqual(r.status_code, 200)
        self.assertTrue(conversation.needs_submit())
        self.assertFalse(conversation.unlocked(request.user))
        #new_request = self.factory.post(
        #    "/pages/%s/edit/%s/" % (self.hierarchy.name, self.section.slug),
        #    {"label": "new conversation label",
        #     "description": "new conversation description"})
        #new_request.user  = self.user
        #data = ""
        #conversation.edit(new_request, data)
        #self.assertEqual(r.status_code, 200)
