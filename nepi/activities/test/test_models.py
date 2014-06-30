from factories import UserFactory, ConversationScenarioFactory
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
        user = User.objects.create_user(
            'person', 'email@emailperson.com', 'personpassword')
        user.save()
        good_conversation = Conversation.objects.create()
        good_conversation.save()
        bad_conversation = Conversation.objects.create()
        bad_conversation.save()
        scenario = ConversationScenario.objects.create(good_conversation=good_conversation, bad_conversation=bad_conversation)
        scenario.save()
        click = ConvClick.objects.create(conversation=good_conversation)
        click.save()
        response = ConversationResponse.objects.create(
            conv_scen=scenario, user=user, first_click=click)
        response.save()
        self.assertIn(response, user.conversationresponse_set.all())
        self.assertEqual(response.first_click, click)


    def test_second_click(self):
        '''testing first click of response object'''
        user = User.objects.create_user(
            'person', 'email@emailperson.com', 'personpassword')
        user.save()
        good_conversation = Conversation.objects.create()
        good_conversation.save()
        bad_conversation = Conversation.objects.create()
        bad_conversation.save()
        scenario = ConversationScenario.objects.create(good_conversation=good_conversation, bad_conversation=bad_conversation)
        scenario.save()
        click_one = ConvClick.objects.create(conversation=good_conversation)
        click_one.save()
        click_two = ConvClick.objects.create(conversation=bad_conversation)
        click_two.save()
        response = ConversationResponse.objects.create(
            conv_scen=scenario, user=user, first_click=click_one, second_click=click_two)
        response.save()
        self.assertIn(response, user.conversationresponse_set.all())
        self.assertEqual(response.first_click, click_one)
        self.assertEqual(response.second_click, click_two)


#     def test_last_response(self):
#         user = User.objects.create_user(
#             'person', 'email@emailperson.com', 'personpassword')
#         user.save()
#         good_conversation = Conversation.objects.create()
#         good_conversation.save()
#         bad_conversation = Conversation.objects.create()
#         bad_conversation.save()
#         scenario = ConversationScenario.objects.create(good_conversation=good_conversation, bad_conversation=bad_conversation)
#         scenario.save()
#         click_one = ConvClick.objects.create(conversation=good_conversation)
#         click_one.save()
#         click_two = ConvClick.objects.create(conversation=bad_conversation)
#         click_two.save()
#         click_three = ConvClick.objects.create(conversation=bad_conversation)
#         click_three.save()
#         click_four = ConvClick.objects.create(conversation=bad_conversation)
#         click_four.save()
#         response = ConversationResponse.objects.create(
#             conv_scen=scenario, user=user, first_click=click_one, second_click=click_two)
#         response.save()
#         self.assertIn(response, user.conversationresponse_set.all())
#         self.assertEqual(response.first_click, click_one)
#         self.assertEqual(response.second_click, click_two)


#     def unlocked(self, user):
#         '''We want to make sure the user has selected both dialogs
#            from the conversation before they can proceed.'''
#         response = ConversationResponse.objects.filter(
#             conv_scen=self, user=user)
#         if (len(response) == 1
#                 and response[0].first_click is not None
#                 and response[0].second_click is not None):
#             return True
#         else:
#             return False
# 
#     def last_response(self, user):
#         try:
#             response = ConversationResponse.objects.get(
#                 conv_scen=self, user=user)
#             if (response.first_click is not None
#                     and response.second_click is not None):
#                 return response.third_click.conversation.scenario_type
#             elif (response.first_click is not None
#                     and response.second_click is None):
#                 return response.first_click.conversation.scenario_type
#         except ConversationResponse.DoesNotExist:
#             return 0


class TestConversation(TestCase):
    def test_unicode(self):
        pass
