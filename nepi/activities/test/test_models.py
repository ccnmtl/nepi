from factories import UserFactory, ConversationScenarioFactory, \
                      GoodConversationFactory, BadConversationFactory, \
                      ConvClickFactory
from factories import ConversationResponseFactory
from django.contrib.auth.models import User
from django.test import TestCase
from nepi.activities.models import ConversationScenario, \
    Conversation, ConversationResponse, ConvClick


class TestConversationScenario(TestCase):
    '''We want to make sure we can create a conversation
     response associated with the user upon submission.'''        
        
    def test_first_click(self):
        '''testing first click of response object'''
        user = UserFactory()
        good_conversation = GoodConversationFactory()
        bad_conversation = BadConversationFactory()
        scenario = ConversationScenarioFactory()
        first_click = ConvClickFactory()
        response = ConversationResponse.objects.create(
            conv_scen=scenario, user=user, first_click=first_click)
        response.save()
        self.assertIn(response, user.conversationresponse_set.all())
        self.assertEqual(response.first_click, first_click)


    def test_second_click(self):
        '''testing second click of response object'''
        user = UserFactory()
        good_conversation = GoodConversationFactory()
        bad_conversation = BadConversationFactory()
        scenario = ConversationScenarioFactory()
        click_one = ConvClickFactory()
        click_two = ConvClickFactory()
        response = ConversationResponse.objects.create(
            conv_scen=scenario, user=user, first_click=click_one, second_click=click_two)
        response.save()
        self.assertIn(response, user.conversationresponse_set.all())
        self.assertEqual(response.first_click, click_one)
        self.assertEqual(response.second_click, click_two)
