from django.contrib.auth.models import User
from django.test.testcases import TestCase
from nepi.main.templatetags.quizscore import is_user_correct, aggregate_score
from quizblock.models import Quiz, Question, Submission, Response, Answer


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


# class TestAccessible(TestCase):
#
#     def setUp(self):
#         self.user = User.objects.create(username="testuser")
#
#     def assert_render_true(self):
#         nl1 = MockNodeList()
#         nl2 = MockNodeList()
#
#         node = AccessibleNode('quiz', nl1, nl2)
#         self.request.user = self.user
#         context = dict(request=self.request, quiz=self.quiz)
#         out = node.render(context)
#         self.assertEqual(out, None)
#         self.assertTrue(nl1.rendered)
#         self.assertFalse(nl2.rendered)
#
#     def assert_render_false(self):
#         nl1 = MockNodeList()
#         nl2 = MockNodeList()
#         node = AccessibleNode('quiz', nl1, nl2)
#         self.request.user = self.user
#         context = dict(request=self.request, quiz=self.quiz)
#         out = node.render(context)
#         self.assertEqual(out, None)
#         self.assertFalse(nl1.rendered)
#         self.assertTrue(nl2.rendered)
#
#     def test_quiz_complete(self):
#         ques1 = Question.objects.create(quiz=self.quiz, text="question_one",
#                                         question_type="single choice")
#         Answer.objects.create(question=ques1, label="a",
#                               value="a", correct=True)
#         Answer.objects.create(question=ques1, label="b", value="b")
#
#         ques2 = Question.objects.create(quiz=self.quiz, text="question_two",
#                                         question_type="multiple choice")
#         Answer.objects.create(question=ques2, label="a",
#                               value="a", correct=True)
#         Answer.objects.create(question=ques2, label="b", value="b")
#         Answer.objects.create(question=ques2, label="c",
#                               value="c", correct=True)
#
#         # No submission
#         self.assert_render_false()
