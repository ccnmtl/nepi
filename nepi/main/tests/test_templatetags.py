from django.contrib.auth.models import User
from django.test.client import RequestFactory
from django.test.testcases import TestCase
from nepi.main.templatetags.accessible import SubmittedNode
from nepi.main.templatetags.progressreport import is_user_correct, \
    aggregate_score
from nepi.main.tests.factories import UserFactory
from pagetree.models import Section, Hierarchy
from pagetree.tests.factories import ModuleFactory
from quizblock.models import Quiz, Question, Submission, Response, Answer
from quizblock.tests.test_templatetags import MockNodeList


class TestIsUserCorrect(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.quiz = Quiz.objects.create()

    def test_short_text(self):
        question = Question.objects.create(quiz=self.quiz,
                                           text="question_one",
                                           question_type="short text")

        self.assertFalse(is_user_correct(question, self.user))

        sub = Submission.objects.create(quiz=self.quiz, user=self.user)
        Response.objects.create(question=question, submission=sub, value="a")

        self.assertTrue(is_user_correct(question, self.user))

    def test_long_text(self):
        question = Question.objects.create(quiz=self.quiz,
                                           text="question_one",
                                           question_type="long text")

        self.assertFalse(is_user_correct(question, self.user))

        sub = Submission.objects.create(quiz=self.quiz, user=self.user)
        Response.objects.create(question=question, submission=sub, value="b")

        self.assertTrue(is_user_correct(question, self.user))

    def test_single_choice_no_correct_answers(self):
        question = Question.objects.create(quiz=self.quiz,
                                           text="question_one",
                                           question_type="single choice")
        Answer.objects.create(question=question, label="a", value="a")
        Answer.objects.create(question=question, label="b", value="b")
        Answer.objects.create(question=question, label="c", value="c")

        # no response
        self.assertFalse(is_user_correct(question, self.user))

        # user responded
        sub = Submission.objects.create(quiz=self.quiz, user=self.user)
        Response.objects.create(question=question, submission=sub, value="b")

        self.assertTrue(is_user_correct(question, self.user))

    def test_single_choice_correct_answers(self):
        question = Question.objects.create(quiz=self.quiz,
                                           text="question_one",
                                           question_type="single choice")
        Answer.objects.create(question=question, label="a", value="a",
                              correct=True)
        Answer.objects.create(question=question, label="b", value="b")
        Answer.objects.create(question=question, label="c", value="c")

        # no response
        self.assertFalse(is_user_correct(question, self.user))

        # user responded
        sub = Submission.objects.create(quiz=self.quiz, user=self.user)
        response = Response.objects.create(question=question,
                                           submission=sub, value="a")

        self.assertTrue(is_user_correct(question, self.user))

        response.value = 'b'
        response.save()
        self.assertFalse(is_user_correct(question, self.user))

    def test_multiple_choice_correct_answers(self):
        question = Question.objects.create(quiz=self.quiz,
                                           text="question_one",
                                           question_type="multiple choice")
        Answer.objects.create(question=question, label="a", value="a",
                              correct=True)
        Answer.objects.create(question=question, label="b", value="b",
                              correct=True)
        Answer.objects.create(question=question, label="c", value="c")

        # no response
        self.assertFalse(is_user_correct(question, self.user))

        # user responded - incorrectly
        sub = Submission.objects.create(quiz=self.quiz, user=self.user)
        c = Response.objects.create(question=question,
                                    submission=sub, value="c")
        self.assertFalse(is_user_correct(question, self.user))

        # user responded - partially incorrectly
        Response.objects.create(question=question, submission=sub, value="a")
        self.assertFalse(is_user_correct(question, self.user))

        # user responded - partially incorrectly
        Response.objects.create(question=question, submission=sub, value="b")
        self.assertFalse(is_user_correct(question, self.user))

        # kill the incorrect one
        c.delete()
        self.assertTrue(is_user_correct(question, self.user))


class TestAggregateQuizScoreFilter(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.quiz1 = Quiz.objects.create()
        self.quiz2 = Quiz.objects.create()
        self.quizzes = Quiz.objects.all()

        # 4 questions
        self.single = Question.objects.create(quiz=self.quiz1,
                                              text="single answer",
                                              question_type="single choice")
        Answer.objects.create(question=self.single, label="a", value="a",
                              correct=True)
        Answer.objects.create(question=self.single, label="b", value="b")

        self.multiple = Question.objects.create(
            quiz=self.quiz1, text="multiple answer",
            question_type="multiple choice")
        Answer.objects.create(question=self.multiple, label="a", value="a",
                              correct=True)
        Answer.objects.create(question=self.multiple, label="b", value="b",
                              correct=True)
        Answer.objects.create(question=self.multiple, label="c", value="c")

        self.short_text = Question.objects.create(quiz=self.quiz2,
                                                  text="short text",
                                                  question_type="short text")

        self.long_text = Question.objects.create(quiz=self.quiz2,
                                                 text="long text",
                                                 question_type="long text")

    def test_no_responses(self):
        self.assertEquals(aggregate_score(self.quizzes, self.user), 0)

    def test_incomplete_one(self):
        submission = Submission.objects.create(quiz=self.quiz1, user=self.user)
        Response.objects.create(question=self.single, submission=submission,
                                value="b")

        submission = Submission.objects.create(quiz=self.quiz2, user=self.user)
        Response.objects.create(question=self.short_text,
                                submission=submission,
                                value="foo")

        self.assertEquals(aggregate_score(self.quizzes, self.user), 25)

    def test_incomplete_two(self):
        submission = Submission.objects.create(quiz=self.quiz1, user=self.user)
        Response.objects.create(question=self.single, submission=submission,
                                value="a")
        Response.objects.create(question=self.multiple, submission=submission,
                                value="a")

        submission = Submission.objects.create(quiz=self.quiz2, user=self.user)
        Response.objects.create(question=self.short_text,
                                submission=submission,
                                value="foo")

        self.assertEquals(aggregate_score(self.quizzes, self.user), 50)

    def test_incomplete_three(self):
        submission = Submission.objects.create(quiz=self.quiz1, user=self.user)
        Response.objects.create(question=self.single, submission=submission,
                                value="a")
        Response.objects.create(question=self.multiple, submission=submission,
                                value="a")
        Response.objects.create(question=self.multiple, submission=submission,
                                value="b")

        submission = Submission.objects.create(quiz=self.quiz2, user=self.user)
        Response.objects.create(question=self.short_text,
                                submission=submission,
                                value="foo")

        self.assertEquals(aggregate_score(self.quizzes, self.user), 75)

    def test_complete(self):
        submission = Submission.objects.create(quiz=self.quiz1, user=self.user)
        Response.objects.create(question=self.single, submission=submission,
                                value="a")
        Response.objects.create(question=self.multiple, submission=submission,
                                value="a")
        Response.objects.create(question=self.multiple, submission=submission,
                                value="b")

        submission = Submission.objects.create(quiz=self.quiz2, user=self.user)
        Response.objects.create(question=self.short_text,
                                submission=submission,
                                value="foo")
        Response.objects.create(question=self.long_text,
                                submission=submission,
                                value="bar")

        self.assertEquals(aggregate_score(self.quizzes, self.user), 100)


class TestAccessible(TestCase):

    def setUp(self):
        self.user = UserFactory(is_superuser=True)

        ModuleFactory("one", "/pages/one/")
        self.hierarchy = Hierarchy.objects.get(name='one')

        self.section_one = Section.objects.get(slug='one')

        self.hierarchy.get_root().add_child_section_from_dict({
            'label': 'Page Four',
            'slug': 'page-four',
            'pageblocks': [{
                'label': 'Content',
                'css_extra': '',
                'block_type': 'Quiz',
                'body': 'random text goes here',
                'description': 'a description',
                'rhetorical': False,
                'questions': [{
                    'question_type': 'short text',
                    'text': 'a question',
                    'explanation': 'an explanation',
                    'intro_text': 'intro text',
                    'answers': []
                }]
            }]
        })
        self.section_four = Section.objects.get(slug='page-four')

        self.request = RequestFactory().get('/pages/%s/' % self.hierarchy.name)
        self.request.user = self.user

    def test_issubmitted_no_pageblocks(self):
        nlTrue = MockNodeList()
        nlFalse = MockNodeList()

        node = SubmittedNode('section', nlTrue, nlFalse)
        context = dict(request=self.request, section=self.section_one)
        out = node.render(context)
        self.assertEqual(out, None)
        self.assertTrue(nlTrue.rendered)
        self.assertFalse(nlFalse.rendered)

    def test_issubmitted_quizblock_nosubmissions(self):
        nlTrue = MockNodeList()
        nlFalse = MockNodeList()

        node = SubmittedNode('section', nlTrue, nlFalse)
        context = dict(request=self.request, section=self.section_four)
        out = node.render(context)
        self.assertEqual(out, None)
        self.assertFalse(nlTrue.rendered)
        self.assertTrue(nlFalse.rendered)

    def test_issubmitted_quizblock_with_submissions(self):
        quiz = Quiz.objects.all()[0]
        question = quiz.question_set.all()[0]
        s = Submission.objects.create(quiz=quiz, user=self.user)
        Response.objects.create(question=question, submission=s, value="a")

        nlTrue = MockNodeList()
        nlFalse = MockNodeList()

        node = SubmittedNode('section', nlTrue, nlFalse)
        context = dict(request=self.request, section=self.section_four)
        out = node.render(context)
        self.assertEqual(out, None)
        self.assertTrue(nlTrue.rendered)
        self.assertFalse(nlFalse.rendered)
