from django.test.client import RequestFactory
from django.test.testcases import TestCase
from pagetree.models import Hierarchy
from pagetree.tests.factories import ModuleFactory
from quizblock.models import Quiz, Question, Answer, Submission, Response

from nepi.activities.models import DosageActivity, DosageActivityResponse, \
    ConversationScenario, ConversationResponse
from nepi.activities.templatetags.adherence_state import GetUserResponse
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

    def test_get_response_with_state(self):
        ConversationResponse.objects.create(user=self.user,
                                            conv_scen=self.block)
        node = ConversationStateNode('block', 'the_response')
        context = dict(request=self.request, block=self.block)
        node.render(context)
        self.assertEquals(context['the_response'], 0)


class TestAdherenceStateNode(TestCase):
    def setUp(self):
        ModuleFactory("one", "/pages/one/")
        self.hierarchy = Hierarchy.objects.get(name='one')
        self.section = self.hierarchy.get_root().get_first_leaf()

        # Setup a quiz block
        self.quiz = Quiz.objects.create()
        self.question = Question.objects.create(
            quiz=self.quiz, text="single", question_type="single choice")
        Answer.objects.create(question=self.question, label="a", value="a",
                              correct=True)
        Answer.objects.create(question=self.question, label="b", value="b")
        self.section.append_pageblock("Quiz One", "adherence", self.quiz)

    def set_quiz_response(self, user, value):
        # complete + right quiz
        submission = Submission.objects.create(quiz=self.quiz, user=user)
        Response.objects.create(question=self.question,
                                submission=submission, value=value)

    def test_get_response_no_state(self):
        request = RequestFactory().get('/pages/%s/' % self.hierarchy.name)
        request.user = UserFactory()

        node = GetUserResponse('adherence', 'the_response')
        context = dict(request=request, section=self.section)
        node.render(context)
        self.assertFalse('the_response' in context)

    def test_get_response_one_submission(self):
        user = UserFactory()
        self.set_quiz_response(user, 'a')

        request = RequestFactory().get('/pages/%s/' % self.hierarchy.name)
        request.user = user

        node = GetUserResponse('adherence', 'the_response')
        context = dict(request=request, section=self.section)
        node.render(context)
        self.assertEquals(context['the_response'], 'a')

    def test_get_response_multiple_submissions(self):
        user = UserFactory()
        self.set_quiz_response(user, 'b')
        self.set_quiz_response(user, 'b')

        request = RequestFactory().get('/pages/%s/' % self.hierarchy.name)
        request.user = user

        node = GetUserResponse('adherence', 'the_response')
        context = dict(request=request, section=self.section)
        node.render(context)
        self.assertEquals(context['the_response'], 'a')
