from django.contrib.auth.models import User
from django.test.client import RequestFactory
from django.test.testcases import TestCase
from pagetree.models import Section, Hierarchy
from pagetree.tests.factories import ModuleFactory
from quizblock.models import Quiz, Question, Submission, Response, Answer
from quizblock.tests.test_templatetags import MockNodeList

from nepi.activities.models import ConversationResponse, ConvClick, \
    DosageActivity, DosageActivityResponse, Day, CalendarResponse
from nepi.activities.tests.factories import ConversationScenarioFactory, \
    MonthFactory, CalendarChartFactory
from nepi.main.templatetags.accessible import SubmittedNode
from nepi.main.templatetags.progressreport import get_scorable_blocks, \
    average_quiz_score, aggregate_scorable_blocks, average_session_score, \
    satisfaction_rating, get_quizzes_by_css_class, get_scorable_content_types
from nepi.main.tests.factories import UserFactory


class TestScorableMethods(TestCase):

    def setUp(self):
        ModuleFactory("one", "/pages/one/")
        self.hierarchy = Hierarchy.objects.get(name='one')
        self.section = self.hierarchy.get_root().get_first_leaf()

        # Setup 5 scorable blocks
        # quiz
        self.quiz = Quiz.objects.create()
        self.question = Question.objects.create(
            quiz=self.quiz, text="single", question_type="single choice")
        Answer.objects.create(question=self.question, label="a", value="a",
                              correct=True)
        Answer.objects.create(question=self.question, label="b", value="b")
        self.section.append_pageblock("Quiz One", "", self.quiz)

        # pretest
        pretest = Quiz.objects.create()
        pretestq = Question.objects.create(
            quiz=pretest, text="single", question_type="single choice")
        Answer.objects.create(question=pretestq, label="a", value="a",
                              correct=True)
        Answer.objects.create(question=pretestq, label="b", value="b")
        self.section.append_pageblock("Pretest", "pretest", pretest)

        # conversation
        self.scenario = ConversationScenarioFactory()
        good_click = ConvClick.objects.create(
            conversation=self.scenario.good_conversation)
        bad_click = ConvClick.objects.create(
            conversation=self.scenario.bad_conversation)
        self.section.append_pageblock("Conversation", "bar", self.scenario)

        # dosage activity
        self.dosage = DosageActivity.objects.create(
            ml_nvp=0.4, times_day=2, weeks=1)
        self.section.append_pageblock("Dosage", "", self.dosage)

        # calendar activity
        month = MonthFactory()
        self.chart = CalendarChartFactory(month=month)
        chart_good_click = Day.objects.create(calendar=month, number=4)
        self.section.append_pageblock("Calendar", "", self.chart)

        self.userNoAnswers = UserFactory()
        self.userIncomplete = UserFactory()
        self.set_quiz_response(self.quiz, self.question,
                               self.userIncomplete, 'b')
        self.set_conversation_response(self.userIncomplete,
                                       good_click, bad_click)

        self.userBadScore = UserFactory()
        self.set_quiz_response(pretest, pretestq, self.userBadScore, 'b')
        self.set_quiz_response(self.quiz, self.question,
                               self.userBadScore, 'a')
        self.set_conversation_response(self.userBadScore,
                                       bad_click, good_click)
        self.set_dosage_response(self.userBadScore, 0.4, 2, 2)
        self.set_calendar_response(self.userBadScore,
                                   chart_good_click, chart_good_click)

        self.userGoodScore = UserFactory()
        self.set_quiz_response(pretest, pretestq, self.userGoodScore, 'a')
        self.set_quiz_response(self.quiz, self.question,
                               self.userGoodScore, 'a')
        self.set_conversation_response(self.userGoodScore,
                                       good_click, bad_click)
        self.set_dosage_response(self.userGoodScore, 0.4, 2, 1)
        self.set_calendar_response(self.userGoodScore,
                                   chart_good_click, chart_good_click)

    def set_quiz_response(self, quiz, question, user, value):
        # complete + right quiz
        submission = Submission.objects.create(quiz=quiz, user=user)
        Response.objects.create(question=question,
                                submission=submission, value=value)

    def set_conversation_response(self, user, first_click, second_click):
        ConversationResponse.objects.create(user=user,
                                            conv_scen=self.scenario,
                                            first_click=first_click,
                                            second_click=second_click)

    def set_dosage_response(self, user, ml_nvp, times_day, weeks):
        DosageActivityResponse.objects.create(user=user,
                                              dosage_activity=self.dosage,
                                              ml_nvp=ml_nvp,
                                              times_day=times_day,
                                              weeks=weeks)

    def set_calendar_response(self, user, first_click, correct_click):
        CalendarResponse.objects.create(user=user,
                                        calendar_activity=self.chart,
                                        first_click=first_click,
                                        correct_click=correct_click)

    def test_get_scorable_blocks(self):
        types = get_scorable_content_types()

        root = self.hierarchy.get_root()
        blocks = get_scorable_blocks(root, types)
        self.assertEquals(len(blocks), 4)
        self.assertEquals(blocks[0].label, "Quiz One")
        self.assertEquals(blocks[1].label, "Conversation")
        self.assertEquals(blocks[2].label, "Dosage")
        self.assertEquals(blocks[3].label, "Calendar")

        blocks = get_quizzes_by_css_class(self.hierarchy, "pretest")
        self.assertEquals(blocks.count(), 1)
        self.assertEquals(blocks[0].label, "Pretest")

    def test_get_no_scorable_blocks(self):
        types = get_scorable_content_types()
        blocks = get_scorable_blocks(Section.objects.get(slug='two'), types)
        self.assertEquals(len(blocks), 0)

    def test_aggregate_scorable_blocks_no_answers(self):
        types = get_scorable_content_types()
        blocks = get_scorable_blocks(self.hierarchy.get_root(), types)
        users = [self.userNoAnswers]
        (score, completed) = aggregate_scorable_blocks(users, blocks)
        self.assertEquals(score, 0)
        self.assertEquals(completed, 0)

    def test_aggregate_scorable_blocks_incomplete(self):
        types = get_scorable_content_types()
        blocks = get_scorable_blocks(self.hierarchy.get_root(), types)
        users = [self.userIncomplete]
        (score, completed) = aggregate_scorable_blocks(users, blocks)
        self.assertEquals(score, 0)
        self.assertEquals(completed, 0)

    def test_aggregate_scorable_blocks_badscore(self):
        types = get_scorable_content_types()
        blocks = get_scorable_blocks(self.hierarchy.get_root(), types)
        users = [self.userBadScore]
        (score, completed) = aggregate_scorable_blocks(users, blocks)
        self.assertEquals(score, .50)
        self.assertEquals(completed, 4)

    def test_aggregate_scorable_blocks_goodscore(self):
        types = get_scorable_content_types()
        blocks = get_scorable_blocks(self.hierarchy.get_root(), types)
        users = [self.userGoodScore]
        (score, completed) = aggregate_scorable_blocks(users, blocks)
        self.assertEquals(score, 1)
        self.assertEquals(completed, 4)

    def test_aggregate_scorable_blocks_all(self):
        types = get_scorable_content_types()
        root = self.hierarchy.get_root()
        blocks = get_scorable_blocks(root, types)
        users = [self.userNoAnswers, self.userIncomplete,
                 self.userBadScore, self.userGoodScore]
        (score, completed) = aggregate_scorable_blocks(users, blocks)
        self.assertEquals(score, .75)
        self.assertEquals(completed, 8)

    def test_average_session_scores(self):
        users = [self.userNoAnswers, self.userIncomplete,
                 self.userBadScore, self.userGoodScore]

        ctx = average_session_score(users, self.hierarchy)
        self.assertEquals(ctx['sessions'][0], 75)
        self.assertEquals(ctx['sessions'][1], None)
        self.assertEquals(ctx['sessions'][2], None)
        self.assertEquals(ctx['average_score'], 75.0)

    def test_average_session_score_incomplete(self):
        users = [self.userIncomplete, self.userNoAnswers]
        ctx = average_session_score(users, self.hierarchy)
        self.assertEquals(ctx['sessions'][0], -1)
        self.assertEquals(ctx['sessions'][1], None)
        self.assertEquals(ctx['sessions'][2], None)
        self.assertTrue('average_score' not in ctx)


class TestAverageQuizScore(TestCase):

    def setUp(self):
        ModuleFactory("one", "/pages/one/")
        self.hierarchy = Hierarchy.objects.get(name='one')
        self.section = self.hierarchy.get_root().get_first_leaf()

        self.user = User.objects.create(username="testuser")
        self.user2 = User.objects.create(username="testuser2")

        self.quiz1 = Quiz.objects.create()
        self.quiz2 = Quiz.objects.create()
        self.section.append_pageblock("Quiz One", 'foo', self.quiz1)
        self.section.append_pageblock("Quiz Two", 'foo', self.quiz2)

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
        # considered incomplete
        self.assertEquals(average_quiz_score([self.user],
                                             self.hierarchy,
                                             'foo'), -1)

    def test_incomplete_one(self):
        submission = Submission.objects.create(quiz=self.quiz1, user=self.user)
        Response.objects.create(question=self.single, submission=submission,
                                value="b")

        submission = Submission.objects.create(quiz=self.quiz2, user=self.user)
        Response.objects.create(question=self.short_text,
                                submission=submission,
                                value="foo")

        self.assertEquals(average_quiz_score([self.user],
                                             self.hierarchy,
                                             'foo'), -1)

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

        self.assertEquals(average_quiz_score([self.user],
                                             self.hierarchy,
                                             'foo'), -1)

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

        self.assertEquals(average_quiz_score([self.user],
                                             self.hierarchy,
                                             'foo'), -1)

    def test_complete(self):
        submission = Submission.objects.create(
            quiz=self.quiz1, user=self.user2)
        Response.objects.create(question=self.single, submission=submission,
                                value="b")

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

        self.assertEquals(average_quiz_score([self.user],
                                             self.hierarchy,
                                             'foo'), 100)

        self.assertEquals(average_quiz_score([self.user, self.user2],
                                             self.hierarchy,
                                             'foo'), 100)

    def test_complete_one_incorrect(self):
        submission = Submission.objects.create(
            quiz=self.quiz1, user=self.user2)
        Response.objects.create(question=self.single, submission=submission,
                                value="b")

        submission = Submission.objects.create(quiz=self.quiz1, user=self.user)
        Response.objects.create(question=self.single, submission=submission,
                                value="b")
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

        self.assertEquals(average_quiz_score([self.user],
                                             self.hierarchy,
                                             'foo'), 75)

        self.assertEquals(average_quiz_score([self.user, self.user2],
                                             self.hierarchy,
                                             'foo'), 75)

    def test_complete_two_incorrect(self):
        submission = Submission.objects.create(
            quiz=self.quiz1, user=self.user2)
        Response.objects.create(question=self.single, submission=submission,
                                value="b")

        submission = Submission.objects.create(quiz=self.quiz1, user=self.user)
        Response.objects.create(question=self.single, submission=submission,
                                value="b")
        Response.objects.create(question=self.multiple, submission=submission,
                                value="a")
        Response.objects.create(question=self.multiple, submission=submission,
                                value="c")

        submission = Submission.objects.create(quiz=self.quiz2, user=self.user)
        Response.objects.create(question=self.short_text,
                                submission=submission,
                                value="foo")
        Response.objects.create(question=self.long_text,
                                submission=submission,
                                value="bar")

        self.assertEquals(average_quiz_score([self.user],
                                             self.hierarchy,
                                             'foo'), 50)

        self.assertEquals(average_quiz_score([self.user, self.user2],
                                             self.hierarchy,
                                             'foo'), 50)

    def test_multiple_complete_submissions(self):
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

        submission = Submission.objects.create(
            quiz=self.quiz1, user=self.user2)
        Response.objects.create(question=self.single, submission=submission,
                                value="b")
        Response.objects.create(question=self.multiple, submission=submission,
                                value="a")
        Response.objects.create(question=self.multiple, submission=submission,
                                value="c")

        submission = Submission.objects.create(
            quiz=self.quiz2, user=self.user2)
        Response.objects.create(question=self.short_text,
                                submission=submission,
                                value="foo")
        Response.objects.create(question=self.long_text,
                                submission=submission,
                                value="bar")

        self.assertEquals(average_quiz_score([self.user, self.user2],
                                             self.hierarchy,
                                             'foo'), 75)


class TestSatisfactionRating(TestCase):

    def setUp(self):
        ModuleFactory("one", "/pages/one/")
        self.hierarchy = Hierarchy.objects.get(name='one')
        section = self.hierarchy.get_root().get_first_leaf()

        self.user = User.objects.create(username="testuser")
        self.user2 = User.objects.create(username="testuser2")

        self.quiz = Quiz.objects.create()
        section.append_pageblock("Quiz One", "satisfaction", self.quiz)

        # 2 questions
        self.question = Question.objects.create(quiz=self.quiz,
                                                text="single answer",
                                                question_type="single choice")
        Answer.objects.create(question=self.question, label="1", value="1")
        Answer.objects.create(question=self.question, label="4", value="4")
        Answer.objects.create(question=self.question, label="5", value="5")

        Question.objects.create(quiz=self.quiz, text="s",
                                question_type="long text")

    def test_no_responses(self):
        rating = satisfaction_rating([self.user, self.user2], self.hierarchy)
        self.assertEquals(rating, None)

    def test_one_complete(self):
        submission = Submission.objects.create(quiz=self.quiz, user=self.user)
        Response.objects.create(question=self.question,
                                submission=submission, value="4")
        rating = satisfaction_rating([self.user, self.user2], self.hierarchy)
        self.assertEquals(rating, 100)

    def test_two_complete(self):
        submission = Submission.objects.create(quiz=self.quiz, user=self.user)
        Response.objects.create(question=self.question,
                                submission=submission, value="5")
        submission = Submission.objects.create(quiz=self.quiz, user=self.user2)
        Response.objects.create(question=self.question,
                                submission=submission, value="1")
        rating = satisfaction_rating([self.user, self.user2], self.hierarchy)
        self.assertEquals(rating, 50)


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
