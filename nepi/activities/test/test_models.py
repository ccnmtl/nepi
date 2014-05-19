from factories import UserFactory, ConversationScenarioFactory
from factories import ConversationResponseFactory
from django.contrib.auth.models import User
from django.test import TestCase
from nepi.activities.models import ConversationScenario, \
    Conversation, ConversationResponse, ConvClick


class TestConversationScenario(TestCase):
    '''We want to make sure we can create a conversation
     response associated with the user upon submission.'''
    def test_submission(self):
        user = User.objects.create_user(
            'person', 'email@emailperson.com', 'personpassword')
        user.save()
        scenario = ConversationScenario.objects.create()
        scenario.save()
        conversation = Conversation.objects.create()
        conversation.save()
        click = ConvClick.objects.create(conversation=conversation)
        click.save()
        response = ConversationResponse.objects.create(
            conv_scen=scenario, user=user, first_click=click)
        response.save()

    def test_first_submission(self):
        # on first user submission - no
        # conversation response has been created yet
        ConversationScenarioFactory()
        UserFactory()
        ConversationResponseFactory()


class TestConversation(TestCase):
    def test_unicode(self):
        pass
