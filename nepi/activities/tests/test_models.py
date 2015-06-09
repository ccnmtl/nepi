from django.test import TestCase
from quizblock.tests.test_models import FakeReq

from factories import ConversationScenarioFactory, ConvClickFactory, \
    GoodConversationFactory, ConversationPageblockHierarchyFactory, \
    ImageInteractiveFactory, ARTCardFactory, AdherenceCardFactory
from nepi.activities.models import ConversationResponse, Day, Month, \
    RetentionClick, Conversation, ConvClick, CalendarResponse, \
    DosageActivityResponse, DosageActivity, ImageInteractive, AdherenceCard, \
    ARTCard, ConversationScenario, RetentionRateCard, CalendarChart
from nepi.activities.tests.factories import CalendarChartFactory, MonthFactory, \
    RetentionRateCardFactory, CorrectDayFactory, DosageActivityFactory
from nepi.main.tests.factories import UserFactory


class TestConvClick(TestCase):
    def test_unicode(self):
        c = ConvClickFactory()
        self.assertEqual(str(c), "G Click")


class TestConversation(TestCase):
    def test_rest_of_conversation(self):
        g = GoodConversationFactory()
        self.assertEqual(str(g.text_one),
                         "We assume text one is the starting text")
        self.assertEqual(
            str(g.response_one),
            "Text 1 is the response to whatever the other party says")
        self.assertEqual(
            str(g.response_two),
            "Text 2 is the response to whatever the other party says")

    def test_unicode(self):
        g = GoodConversationFactory()
        self.assertEqual(str(g), "G")


class TestConversationScenario(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.scenario = ConversationScenarioFactory()
        self.good = ConvClick.objects.create(
            conversation=self.scenario.good_conversation)
        self.bad = ConvClick.objects.create(
            conversation=self.scenario.bad_conversation)

    def test_unicode(self):
        c = ConversationPageblockHierarchyFactory()
        self.assertEqual(str(c), "conv_hierarchy")

    def test_as_dict(self):
        d = self.scenario.as_dict()
        self.assertEquals(self.scenario.description, d['description'])

        good = d['good_conversation']
        self.assertEquals(self.scenario.good_conversation.scenario_type,
                          good['scenario_type'])
        self.assertEquals(self.scenario.good_conversation.text_one,
                          good['text_one'])
        self.assertEquals(self.scenario.good_conversation.response_one,
                          good['response_one'])
        self.assertEquals(self.scenario.good_conversation.response_two,
                          good['response_two'])
        self.assertEquals(self.scenario.good_conversation.response_three,
                          good['response_three'])
        self.assertEquals(self.scenario.good_conversation.complete_dialog,
                          good['complete_dialog'])

        bad = d['bad_conversation']
        self.assertEquals(self.scenario.bad_conversation.scenario_type,
                          bad['scenario_type'])
        self.assertEquals(self.scenario.bad_conversation.text_one,
                          bad['text_one'])
        self.assertEquals(self.scenario.bad_conversation.response_one,
                          bad['response_one'])
        self.assertEquals(self.scenario.bad_conversation.response_two,
                          bad['response_two'])
        self.assertEquals(self.scenario.bad_conversation.response_three,
                          bad['response_three'])
        self.assertEquals(self.scenario.bad_conversation.complete_dialog,
                          bad['complete_dialog'])

    def test_create_from_dict(self):
        d = self.scenario.as_dict()
        block = ConversationScenario.create_from_dict(d)
        self.assertEquals(block.description, self.scenario.description)

        good = block.good_conversation
        self.assertEquals(self.scenario.good_conversation.scenario_type,
                          good.scenario_type)
        self.assertEquals(self.scenario.good_conversation.text_one,
                          good.text_one)
        self.assertEquals(self.scenario.good_conversation.response_one,
                          good.response_one)
        self.assertEquals(self.scenario.good_conversation.response_two,
                          good.response_two)
        self.assertEquals(self.scenario.good_conversation.response_three,
                          good.response_three)
        self.assertEquals(self.scenario.good_conversation.complete_dialog,
                          good.complete_dialog)

        bad = block.bad_conversation
        self.assertEquals(self.scenario.good_conversation.scenario_type,
                          bad.scenario_type)
        self.assertEquals(self.scenario.good_conversation.text_one,
                          bad.text_one)
        self.assertEquals(self.scenario.good_conversation.response_one,
                          bad.response_one)
        self.assertEquals(self.scenario.good_conversation.response_two,
                          bad.response_two)
        self.assertEquals(self.scenario.good_conversation.response_three,
                          bad.response_three)
        self.assertEquals(self.scenario.good_conversation.complete_dialog,
                          bad.complete_dialog)

    def test_add_form(self):
        self.assertTrue("description" in self.scenario.add_form().fields)

    def test_score_incomplete(self):
        self.assertEquals(self.scenario.score(self.user), None)

        resp = ConversationResponse.objects.create(user=self.user,
                                                   conv_scen=self.scenario)
        self.assertEquals(self.scenario.score(self.user), None)

        resp.first_click = self.good
        resp.save()
        self.assertEquals(self.scenario.score(self.user), None)

    def test_score_correct(self):
        ConversationResponse.objects.create(user=self.user,
                                            conv_scen=self.scenario,
                                            first_click=self.good,
                                            second_click=self.bad)
        self.assertEquals(self.scenario.score(self.user), 1)

    def test_score_incorrect(self):
        ConversationResponse.objects.create(user=self.user,
                                            conv_scen=self.scenario,
                                            first_click=self.bad,
                                            second_click=self.good)
        self.assertEquals(self.scenario.score(self.user), 0)


class TestLRConversationScenario(TestCase):
    '''We want to make sure we can create a conversation
     response associated with the user upon submission.'''

    def test_last_response_and_unlocked(self):
        '''testing assert click of response object'''
        user = UserFactory()
        scenario = ConversationScenarioFactory()
        click_one = ConvClickFactory(conversation=scenario.good_conversation)
        click_two = ConvClickFactory(conversation=scenario.bad_conversation)
        click_three = ConvClickFactory(conversation=scenario.good_conversation)

        # No Clicks
        self.assertFalse(scenario.unlocked(user))
        self.assertEquals(scenario.last_response(user), 0)

        '''Test first click'''
        cr = ConversationResponse.objects.create(conv_scen=scenario,
                                                 user=user,
                                                 first_click=click_one)
        self.assertEquals(click_one.conversation.scenario_type,
                          cr.first_click.conversation.scenario_type)
        self.assertIsNone(cr.second_click)
        self.assertFalse(scenario.unlocked(user))
        self.assertEquals(scenario.last_response(user),
                          click_one.conversation.scenario_type)

        '''Test second click'''
        cr.second_click = click_two
        cr.save()
        self.assertEquals(click_two.conversation.scenario_type,
                          cr.second_click.conversation.scenario_type)
        self.assertIsNone(cr.third_click)
        self.assertTrue(scenario.unlocked(user))
        self.assertEquals(scenario.last_response(user),
                          click_two.conversation.scenario_type)

        '''Test third click'''
        cr.third_click = click_three
        cr.save()
        self.assertEquals(click_three.conversation.scenario_type,
                          cr.third_click.conversation.scenario_type)
        self.assertIsNotNone(cr.third_click)
        self.assertTrue(scenario.unlocked(user))
        self.assertEquals(scenario.last_response(user),
                          click_three.conversation.scenario_type)

        # Multiple responses - use the first response
        ConversationResponse.objects.create(conv_scen=scenario,
                                            user=user,
                                            first_click=click_one)
        self.assertEquals(scenario.last_response(user),
                          click_three.conversation.scenario_type)

    def test_both_responses_clicked(self):
        user = UserFactory()
        scenario = ConversationScenarioFactory()
        one = ConvClickFactory(conversation=scenario.good_conversation)
        two = ConvClickFactory(conversation=scenario.good_conversation)
        three = ConvClickFactory(conversation=scenario.good_conversation)
        four = ConvClickFactory(conversation=scenario.bad_conversation)

        cr = ConversationResponse.objects.create(conv_scen=scenario,
                                                 user=user,
                                                 first_click=one,
                                                 second_click=two,
                                                 third_click=three)

        self.assertFalse(scenario.unlocked(user))

        cr.third_click = four
        cr.save()

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

    def test_as_dict(self):
        block = DosageActivityFactory()
        d = block.as_dict()
        self.assertEquals(block.explanation, d['explanation'])
        self.assertEquals(block.question, d['question'])
        self.assertEquals(block.ml_nvp, d['ml_nvp'])
        self.assertEquals(block.times_day, d['times_day'])
        self.assertEquals(block.weeks, d['weeks'])

    def test_create_from_dict(self):
        original = DosageActivityFactory()
        duplicate = DosageActivity.create_from_dict(original.as_dict())

        self.assertEquals(original.explanation, duplicate.explanation)
        self.assertEquals(original.question, duplicate.question)
        self.assertEquals(original.ml_nvp, duplicate.ml_nvp)
        self.assertEquals(original.times_day, duplicate.times_day)
        self.assertEquals(original.weeks, duplicate.weeks)


class TestDayAndMonthObjects(TestCase):
    def setUp(self):
        self.m = Month(display_name="June")
        self.d = Day(calendar=self.m, number=1, explanation="Your wrong!")

    def test_unicode(self):
        self.assertEqual(str(self.m), "June in None")
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

    def test_unlocked(self):
        user = UserFactory()
        month = MonthFactory()
        chart = CalendarChartFactory(month=month)

        self.assertFalse(chart.unlocked(user))

        resp = CalendarResponse.objects.create(user=user,
                                               calendar_activity=chart)
        self.assertFalse(chart.unlocked(user))

        clk = Day.objects.create(calendar=month, number=2)
        resp.first_click = clk
        resp.save()
        self.assertFalse(chart.unlocked(user))

        clk = Day.objects.create(calendar=month, number=4)
        resp.correct_click = clk
        resp.save()
        self.assertTrue(chart.unlocked(user))

    def test_score(self):
        user = UserFactory()
        month = MonthFactory()
        chart = CalendarChartFactory(month=month)

        self.assertEquals(chart.score(user), None)

        resp = CalendarResponse.objects.create(user=user,
                                               calendar_activity=chart)
        self.assertEquals(chart.score(user), None)

        incorrect = Day.objects.create(calendar=month, number=1)
        resp.first_click = incorrect
        resp.save()
        self.assertEquals(chart.score(user), None)

        correct = Day.objects.create(calendar=month, number=4)
        resp.correct_click = correct
        resp.save()
        self.assertEquals(chart.score(user), 0)

        resp.first_click = correct
        resp.save()
        self.assertEquals(chart.score(user), 1)

    def test_as_dict(self):
        day = CorrectDayFactory()
        chart = CalendarChartFactory(month=day.calendar)

        d = chart.as_dict()
        self.assertEquals(chart.description, d['description'])
        self.assertEquals(chart.correct_date, d['correct_date'])
        self.assertEquals(chart.month.display_name, d['month']['display_name'])
        self.assertEquals(1, len(d['month']['days']))
        self.assertEquals(day.number, d['month']['days'][0]['number'])
        self.assertEquals(day.explanation,
                          d['month']['days'][0]['explanation'])

    def test_create_from_dict(self):
        day = CorrectDayFactory()
        original = CalendarChartFactory(month=day.calendar)
        d = original.as_dict()

        duplicate = CalendarChart.create_from_dict(d)
        self.assertEquals(original.description, duplicate.description)
        self.assertEquals(original.correct_date, duplicate.correct_date)
        self.assertEquals(original.month.display_name,
                          duplicate.month.display_name)
        self.assertEquals(duplicate.month.day_set.count(), 1)

        day2 = duplicate.month.day_set.first()
        self.assertEquals(day.number, day2.number)
        self.assertEquals(day.explanation, day2.explanation)


class TestImageInteractive(TestCase):
    def test_img_int_need_submit(self):
        img_int = ImageInteractiveFactory()
        self.assertFalse(img_int.needs_submit())

    def test_img_int_unlocked(self):
        img_int = ImageInteractiveFactory()
        usr = UserFactory()
        self.assertTrue(img_int.unlocked(usr))

    def test_img_int_add_form(self):
        add_form = ImageInteractiveFactory().add_form()
        self.assertTrue("intro_text" in add_form.fields)

    def test_img_int_edit_form(self):
        edit_form = ImageInteractiveFactory().edit_form()
        self.assertTrue("intro_text" in edit_form.fields)

    def test_img_int_create(self):
        r = FakeReq()
        r.POST = {'intro_text': 'intro_text info here'}
        img_int = ImageInteractive.create(r)
        self.assertEquals(img_int.intro_text, 'intro_text info here')
        self.assertEquals(img_int.display_name, "Image Interactive")

    def test_as_dict(self):
        block = ImageInteractiveFactory()
        d = block.as_dict()
        self.assertEquals(block.intro_text, d['intro_text'])

    def test_create_from_dict(self):
        d = ImageInteractiveFactory().as_dict()
        block = ImageInteractive.create_from_dict(d)
        self.assertEquals(d['intro_text'], block.intro_text)


class TestARTCard(TestCase):
    def test_artcard_need_submit(self):
        artcard = ARTCardFactory()
        self.assertFalse(artcard.needs_submit())

    def test_artcard_unlocked(self):
        artcard = ARTCardFactory()
        usr = UserFactory()
        self.assertTrue(artcard.unlocked(usr))

    def test_artcard_add_form(self):
        add_form = ARTCardFactory().add_form()
        self.assertTrue("intro_text" in add_form.fields)

    def test_artcard_edit_form(self):
        edit_form = ARTCardFactory().edit_form()
        self.assertTrue("intro_text" in edit_form.fields)

    def test_artcard_create(self):
        r = FakeReq()
        r.POST = {'intro_text': 'intro_text info here'}
        artcard = ARTCard.create(r)
        self.assertEquals(artcard.intro_text, 'intro_text info here')
        self.assertEquals(artcard.display_name, "ART Card")

    def test_as_dict(self):
        block = ARTCardFactory()
        d = block.as_dict()
        self.assertEquals(block.intro_text, d['intro_text'])

    def test_create_from_dict(self):
        d = ARTCardFactory().as_dict()
        block = ARTCard.create_from_dict(d)
        self.assertEquals(d['intro_text'], block.intro_text)


class TestAdherenceCard(TestCase):
    def test_adcard_need_submit(self):
        adcard = AdherenceCardFactory()
        self.assertFalse(adcard.needs_submit())

    def test_adcard_unlocked(self):
        adcard = AdherenceCardFactory()
        usr = UserFactory()
        self.assertTrue(adcard.unlocked(usr))

    def test_adcard_add_form(self):
        add_form = AdherenceCardFactory().add_form()
        self.assertTrue("quiz_class" in add_form.fields)

    def test_adcard_edit_form(self):
        edit_form = AdherenceCardFactory().edit_form()
        self.assertTrue("quiz_class" in edit_form.fields)

    def test_adcard_create(self):
        r = FakeReq()
        r.POST = {'quiz_class': 'intro_text info here'}
        adcard = AdherenceCard.create(r)
        self.assertEquals(adcard.quiz_class, 'intro_text info here')
        self.assertEquals(adcard.display_name, "Adherence Card")

    def test_as_dict(self):
        block = AdherenceCardFactory()
        d = block.as_dict()
        self.assertEquals(block.quiz_class, d['quiz_class'])

    def test_create_from_dict(self):
        d = AdherenceCardFactory().as_dict()
        block = AdherenceCard.create_from_dict(d)
        self.assertEquals(d['quiz_class'], block.quiz_class)


class TestRetentionRateCard(TestCase):

    def test_as_dict(self):
        block = RetentionRateCardFactory()
        d = block.as_dict()
        self.assertEquals(block.intro_text, d['intro_text'])

    def test_create_from_dict(self):
        d = RetentionRateCardFactory().as_dict()
        block = RetentionRateCard.create_from_dict(d)
        self.assertEquals(d['intro_text'], block.intro_text)
