from factories import UserFactory, ConversationScenarioFactory
from factories import ConversationResponseFactory
from django.test import TestCase


class TestConversationScenario(TestCase):
    def test_unicode(self):
        cs = ConversationScenarioFactory()
        # possibilities for submissions
        # it is first user submission - no
        # conversation response has been created yet

        #submit
        # user has clicked on one conversation and clicks on same one
        # user has clicked on both conversations
        # user
        # self.assertEqual(str(cs), "Conversation Scenario")

    def test_first_submission(self):
        # on first user submission - no
        # conversation response has been created yet
        cs = ConversationScenarioFactory()
        user = UserFactory()
        cr = ConversationResponseFactory()
        #cs.submit(user, cr)
        #cr = ConversationResponseFactory()
        #cr.scenario = cs
        #cr.user = user
        #cr.save()


class TestConversation(TestCase):
    def test_unicode(self):
        pass
