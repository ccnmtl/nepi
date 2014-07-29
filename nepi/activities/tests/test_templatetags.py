from django.test.client import RequestFactory
from django.test.testcases import TestCase
from nepi.activities.models import DosageActivity, DosageActivityResponse, \
    ConversationScenario, ConversationResponse
from nepi.activities.templatetags.conversation_state import \
    ConversationStateNode
from nepi.activities.templatetags.dosage_state import DosageStateNode
from nepi.main.tests.factories import UserFactory


class TestDosageStateNode(TestCase):

    def setUp(self):
        self.user = UserFactory(is_superuser=True)

        self.request = RequestFactory().get('/')
        self.request.user = self.user

        self.block = DosageActivity.objects.create()

    def test_get_response_no_state(self):
        node = DosageStateNode('block', 'the_response')
        context = dict(request=self.request, block=self.block)
        node.render(context)
        self.assertIsNone(context['the_response'])

    def test_get_response_with_state(self):
        state = DosageActivityResponse.objects.create(
            user=self.user, dosage_activity=self.block, ml_nvp=10,
            times_day=10, weeks=10)
        node = DosageStateNode('block', 'the_response')
        context = dict(request=self.request, block=self.block)
        node.render(context)
        self.assertEquals(context['the_response'], state)


class TestConversationStateNode(TestCase):
    def setUp(self):
        self.user = UserFactory(is_superuser=True)

        self.request = RequestFactory().get('/')
        self.request.user = self.user

        self.block = ConversationScenario.objects.create()

    def test_get_response_no_state(self):
        node = ConversationStateNode('block', 'the_response')
        context = dict(request=self.request, block=self.block)
        node.render(context)
        self.assertEquals(context['the_response'], 0)

    def test_get_dosage_response_with_state(self):
        ConversationResponse.objects.create(user=self.user,
                                            conv_scen=self.block)
        node = ConversationStateNode('block', 'the_response')
        context = dict(request=self.request, block=self.block)
        node.render(context)
        self.assertEquals(context['the_response'], 0)
