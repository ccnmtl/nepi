from django.test import TestCase
from factories import ConversationScenarioFactory, ConvClickFactory, \
    GoodConversationFactory, ConversationPageblockHierarchyFactory
from nepi.activities.models import ConversationResponse, Day, Month, \
    RetentionClick, Conversation, ConvClick, CalendarResponse, \
    DosageActivityResponse, DosageActivity
from nepi.activities.tests.factories import CalendarChartFactory, MonthFactory
from nepi.main.tests.factories import UserFactory


class TestConvClick(TestCase):
    def test_unicode(self):
        c = ConvClickFactory()
        self.assertEqual(str(c), "G Click")


class TestConversation(TestCase):
    def test_unicode(self):
        g = GoodConversationFactory()
        self.assertEqual(str(g), "G")


class TestConversationScenario(TestCase):

    def test_unicode(self):
        c = ConversationPageblockHierarchyFactory()
        self.assertEqual(str(c), "conv_hierarchy")

    def test_score(self):
        user = UserFactory()
        scenario = ConversationScenarioFactory()

        self.assertEquals(scenario.score(user), None)

        resp = ConversationResponse.objects.create(user=user,
                                                   conv_scen=scenario)
        self.assertEquals(scenario.score(user), None)

        clk = ConvClick.objects.create(conversation=scenario.good_conversation)
        resp.first_click = clk
        resp.save()
        self.assertEquals(scenario.score(user), 1)

        clk = ConvClick.objects.create(conversation=scenario.bad_conversation)
        resp.first_click = clk
        resp.save()
        self.assertEquals(scenario.score(user), 0)


# class TestConversationResponse(TestCase):
#    def test_unicode(self):
#        cr = ConversationResponse(conv_scen = ConversationScenarioFactory(),
#                                         user = UserFactory(),
#                                         first_click = ConvClickFactory(),
#                                         second_click = ConvClickFactory(),
#                                         third_click = ConvClickFactory())
#        # self.assertEqual(str(cr), conv_hierarchy)


class TestLRConversationScenario(TestCase):
    '''We want to make sure we can create a conversation
     response associated with the user upon submission.'''

    def test_last_response_and_unlocked(self):
        '''testing assert click of response object'''
        user = UserFactory()
        scenario = ConversationScenarioFactory()
        click_one = ConvClickFactory()
        click_two = ConvClickFactory()
        click_three = ConvClickFactory()
        '''go through conditionals'''
        with self.assertRaises(ConversationResponse.DoesNotExist):
            ConversationResponse.objects.get(conv_scen=scenario, user=user)
            '''how to we test that the except returns 0?'''
        '''Test first click'''
        cr = ConversationResponse.objects.create(conv_scen=scenario,
                                                 user=user,
                                                 first_click=click_one)
        self.assertEquals(click_one.conversation.scenario_type,
                          cr.first_click.conversation.scenario_type)
        self.assertIsNone(cr.second_click)
        self.assertFalse(scenario.unlocked(user))
        # self.assertTrue(scenario.needs_submit())
        '''Test second click'''
        cr.second_click = click_two
        cr.save()
        self.assertEquals(click_two.conversation.scenario_type,
                          cr.second_click.conversation.scenario_type)
        self.assertIsNone(cr.third_click)
        self.assertTrue(scenario.unlocked(user))
        '''Test third click'''
        cr.third_click = click_three
        cr.save()
        self.assertEquals(click_three.conversation.scenario_type,
                          cr.third_click.conversation.scenario_type)
        self.assertIsNotNone(cr.third_click)
        self.assertTrue(scenario.unlocked(user))


class TestDosageActivity(TestCase):

    def test_score(self):
        user = UserFactory()
        activity = DosageActivity.objects.create(
            ml_nvp=0.4, times_day=2, weeks=1)
        self.assertEquals(activity.score(user), None)

        resp = DosageActivityResponse.objects.create(user=user,
                                                     dosage_activity=activity,
                                                     ml_nvp=1,
                                                     times_day=2,
                                                     weeks=4)
        self.assertEquals(activity.score(user), 0)

        resp.ml_nvp = 0.4
        resp.times_day = 2
        resp.weeks = 1
        resp.save()
        self.assertEquals(activity.score(user), 1)


class TestDayAndMonthObjects(TestCase):
    def setUp(self):
        self.m = Month(display_name="June")
        self.d = Day(calendar=self.m, number=1, explanation="Your wrong!")

    def test_unicode(self):
        self.assertEqual(str(self.m), "June")
        self.assertEqual(str(self.d), "1 Your wrong!")


class TestRetentionResponseAndRetentionClick(TestCase):

    def setUp(self):
        self.retention_click = RetentionClick(click_string="eligible_click")

    def test_unicode(self):
        self.assertEqual(str(self.retention_click),
                         "Click String: eligible_click")

'''Trying to see if not using factory boy makes coverage see the tests'''


class TestConversationNoFactory(TestCase):

    def setUp(self):
        self.test_conversation = Conversation.objects.create()
        self.test_conversation.scenario_type = 'G'
        self.test_conversation.text_one = \
            "We assume text one is the starting text"
        self.test_conversation.response_one = \
            "Text 1 is the response to whatever the other party says"
        self.test_conversation.response_two = \
            "Text 2 is the response to whatever the other party says"
        self.test_conversation.response_three = \
            "Text 3 is an optional response/thought to "
        self.test_conversation.complete_dialog = \
            "This is the entire Nurse/Patient exchange"

    def test_conv_unicode(self):
        self.assertEquals(str(self.test_conversation), 'G')


class TestCalendarChart(TestCase):

    def test_score(self):
        user = UserFactory()
        month = MonthFactory()
        chart = CalendarChartFactory(month=month)

        self.assertEquals(chart.score(user), None)

        resp = CalendarResponse.objects.create(user=user,
                                               calendar_activity=chart)
        self.assertEquals(chart.score(user), None)

        clk = Day.objects.create(calendar=month, number=4)
        resp.first_click = clk
        resp.save()
        self.assertEquals(chart.score(user), 1)

        clk = Day.objects.create(calendar=month, number=1)
        resp.first_click = clk
        resp.save()
        self.assertEquals(chart.score(user), 0)
