from __future__ import unicode_literals

from decimal import Decimal

from django.test import TestCase
from django.utils.encoding import smart_str
from pagetree.tests.factories import HierarchyFactory
from quizblock.tests.test_models import FakeReq

from nepi.activities.models import (
    ConvClick, ConversationResponse, ConversationScenario, DosageActivity,
    DosageActivityResponse, Month, Day, RetentionResponse, RetentionClick,
    RetentionRateCard, Conversation, CalendarResponse, CalendarChart,
    ImageInteractive, ARTCard, AdherenceCard)
from nepi.activities.tests.factories import (
    ConvClickFactory,  GoodConversationFactory, ConversationScenarioFactory,
    DosageActivityFactory, RetentionRateCardFactory, RetentionClickFactory,
    CalendarChartFactory, MonthFactory, CorrectDayFactory,
    ImageInteractiveFactory, ARTCardFactory, AdherenceCardFactory)
from nepi.main.tests.factories import UserFactory
import json


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
        HierarchyFactory().get_root().append_pageblock(
            'test', '', self.scenario)

    def test_basics(self):
        self.assertTrue(smart_str(self.scenario).startswith('Root'))
        self.assertIsNotNone(self.scenario.pageblock())
        self.assertFalse(self.scenario.redirect_to_self_on_submit())
        self.assertTrue(self.scenario.needs_submit())

    def test_clear_user_submissions(self):
        ConversationResponse.objects.create(user=self.user,
                                            conv_scen=self.scenario)
        self.scenario.clear_user_submissions(self.user)

        responses = ConversationResponse.objects.filter(
            user=self.user, conv_scen=self.scenario)
        self.assertEqual(responses.count(), 0)

    def test_edit(self):
        self.scenario.edit({'description': 'updated description'}, None)
        self.assertEqual(self.scenario.description, 'updated description')

    def test_create(self):
        r = FakeReq()
        r.POST = {'description': 'create'}
        artcard = ConversationScenario.create(r)
        self.assertEqual(artcard.description, 'create')

    def test_as_dict(self):
        d = self.scenario.as_dict()
        self.assertEqual(self.scenario.description, d['description'])

        good = d['good_conversation']
        self.assertEqual(self.scenario.good_conversation.scenario_type,
                         good['scenario_type'])
        self.assertEqual(self.scenario.good_conversation.text_one,
                         good['text_one'])
        self.assertEqual(self.scenario.good_conversation.response_one,
                         good['response_one'])
        self.assertEqual(self.scenario.good_conversation.response_two,
                         good['response_two'])
        self.assertEqual(self.scenario.good_conversation.response_three,
                         good['response_three'])
        self.assertEqual(self.scenario.good_conversation.complete_dialog,
                         good['complete_dialog'])

        bad = d['bad_conversation']
        self.assertEqual(self.scenario.bad_conversation.scenario_type,
                         bad['scenario_type'])
        self.assertEqual(self.scenario.bad_conversation.text_one,
                         bad['text_one'])
        self.assertEqual(self.scenario.bad_conversation.response_one,
                         bad['response_one'])
        self.assertEqual(self.scenario.bad_conversation.response_two,
                         bad['response_two'])
        self.assertEqual(self.scenario.bad_conversation.response_three,
                         bad['response_three'])
        self.assertEqual(self.scenario.bad_conversation.complete_dialog,
                         bad['complete_dialog'])

    def test_as_dict_incomplete(self):
        scenario = ConversationScenarioFactory(good_conversation=None,
                                               bad_conversation=None)

        d = scenario.as_dict()
        self.assertEqual(self.scenario.description, d['description'])
        self.assertFalse('good_conversation' in d)
        self.assertFalse('bad_conversation' in d)

    def test_create_from_dict(self):
        d = self.scenario.as_dict()
        block = ConversationScenario.create_from_dict(d)
        self.assertEqual(block.description, self.scenario.description)

        good = block.good_conversation
        self.assertEqual(self.scenario.good_conversation.scenario_type,
                         good.scenario_type)
        self.assertEqual(self.scenario.good_conversation.text_one,
                         good.text_one)
        self.assertEqual(self.scenario.good_conversation.response_one,
                         good.response_one)
        self.assertEqual(self.scenario.good_conversation.response_two,
                         good.response_two)
        self.assertEqual(self.scenario.good_conversation.response_three,
                         good.response_three)
        self.assertEqual(self.scenario.good_conversation.complete_dialog,
                         good.complete_dialog)

        bad = block.bad_conversation
        self.assertEqual(self.scenario.good_conversation.scenario_type,
                         bad.scenario_type)
        self.assertEqual(self.scenario.good_conversation.text_one,
                         bad.text_one)
        self.assertEqual(self.scenario.good_conversation.response_one,
                         bad.response_one)
        self.assertEqual(self.scenario.good_conversation.response_two,
                         bad.response_two)
        self.assertEqual(self.scenario.good_conversation.response_three,
                         bad.response_three)
        self.assertEqual(self.scenario.good_conversation.complete_dialog,
                         bad.complete_dialog)

    def test_add_form(self):
        self.assertTrue("description" in self.scenario.add_form().fields)

    def test_edit_form(self):
        edit_form = self.scenario.edit_form()
        self.assertTrue("description" in edit_form.fields)
        self.assertTrue("update good conversation" in edit_form.alt_text)
        self.assertTrue("update bad conversation" in edit_form.alt_text)

        scenario = ConversationScenarioFactory(good_conversation=None)
        edit_form = scenario.edit_form()
        self.assertTrue("description" in edit_form.fields)
        self.assertTrue("add good conversation" in edit_form.alt_text)
        self.assertTrue("update bad conversation" in edit_form.alt_text)

        scenario = ConversationScenarioFactory(bad_conversation=None)
        edit_form = scenario.edit_form()
        self.assertTrue("description" in edit_form.fields)
        self.assertTrue("update good conversation" in edit_form.alt_text)
        self.assertTrue("add bad conversation" in edit_form.alt_text)

        scenario = ConversationScenarioFactory(good_conversation=None,
                                               bad_conversation=None)
        edit_form = scenario.edit_form()
        self.assertTrue("description" in edit_form.fields)
        self.assertTrue("add good conversation" in edit_form.alt_text)
        self.assertTrue("add bad conversation" in edit_form.alt_text)

    def test_score_incomplete(self):
        self.assertEqual(self.scenario.score(self.user), None)

        resp = ConversationResponse.objects.create(user=self.user,
                                                   conv_scen=self.scenario)
        self.assertEqual(self.scenario.score(self.user), None)

        resp.first_click = self.good
        resp.save()
        self.assertEqual(self.scenario.score(self.user), None)

    def test_score_correct(self):
        ConversationResponse.objects.create(user=self.user,
                                            conv_scen=self.scenario,
                                            first_click=self.good,
                                            second_click=self.bad)
        self.assertEqual(self.scenario.score(self.user), 1)

    def test_score_incorrect(self):
        ConversationResponse.objects.create(user=self.user,
                                            conv_scen=self.scenario,
                                            first_click=self.bad,
                                            second_click=self.good)
        self.assertEqual(self.scenario.score(self.user), 0)

    def test_conversation_response(self):
        r = ConversationResponse.objects.create(user=self.user,
                                                conv_scen=self.scenario,
                                                first_click=self.bad,
                                                second_click=self.good)
        self.assertTrue(smart_str(r).startswith('Response to Root'))


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
        self.assertEqual(scenario.last_response(user), 0)

        '''Test first click'''
        cr = ConversationResponse.objects.create(conv_scen=scenario,
                                                 user=user,
                                                 first_click=click_one)
        self.assertEqual(click_one.conversation.scenario_type,
                         cr.first_click.conversation.scenario_type)
        self.assertIsNone(cr.second_click)
        self.assertFalse(scenario.unlocked(user))
        self.assertEqual(scenario.last_response(user),
                         click_one.conversation.scenario_type)

        '''Test second click'''
        cr.second_click = click_two
        cr.save()
        self.assertEqual(click_two.conversation.scenario_type,
                         cr.second_click.conversation.scenario_type)
        self.assertIsNone(cr.third_click)
        self.assertTrue(scenario.unlocked(user))
        self.assertEqual(scenario.last_response(user),
                         click_two.conversation.scenario_type)

        '''Test third click'''
        cr.third_click = click_three
        cr.save()
        self.assertEqual(click_three.conversation.scenario_type,
                         cr.third_click.conversation.scenario_type)
        self.assertIsNotNone(cr.third_click)
        self.assertTrue(scenario.unlocked(user))
        self.assertEqual(scenario.last_response(user),
                         click_three.conversation.scenario_type)

        # Multiple responses - use the first response
        ConversationResponse.objects.create(conv_scen=scenario,
                                            user=user,
                                            first_click=click_one)
        self.assertEqual(scenario.last_response(user),
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

    def test_basics(self):
        block = DosageActivityFactory()
        HierarchyFactory().get_root().append_pageblock('test', '', block)

        self.assertTrue(smart_str(block).startswith('Root'))
        self.assertIsNotNone(block.pageblock())
        self.assertTrue(block.needs_submit())
        self.assertTrue(block.redirect_to_self_on_submit())

    def test_score(self):
        user = UserFactory()
        activity = DosageActivity.objects.create(
            ml_nvp=0.4, times_day=2, weeks=1)
        self.assertEqual(activity.score(user), None)

        resp = DosageActivityResponse.objects.create(user=user,
                                                     dosage_activity=activity,
                                                     ml_nvp=1,
                                                     times_day=2,
                                                     weeks=4)
        self.assertEqual(activity.score(user), 0)

        resp.ml_nvp = 0.4
        resp.times_day = 2
        resp.weeks = 1
        resp.save()
        self.assertEqual(activity.score(user), 1)

    def test_add_form(self):
        add_form = DosageActivityFactory().add_form()
        self.assertTrue("explanation" in add_form.fields)
        self.assertTrue("question" in add_form.fields)
        self.assertTrue("ml_nvp" in add_form.fields)
        self.assertTrue("times_day" in add_form.fields)
        self.assertTrue("weeks" in add_form.fields)

    def test_edit_form(self):
        edit_form = DosageActivityFactory().edit_form()
        self.assertTrue("explanation" in edit_form.fields)
        self.assertTrue("question" in edit_form.fields)
        self.assertTrue("ml_nvp" in edit_form.fields)
        self.assertTrue("times_day" in edit_form.fields)
        self.assertTrue("weeks" in edit_form.fields)

    def test_create(self):
        r = FakeReq()
        r.POST = {'explanation': 'explanation', 'question': 'question',
                  'ml_nvp': 1.6, 'times_day': 3, 'weeks': 3}
        block = DosageActivity.create(r)
        self.assertEqual(block.explanation, 'explanation')
        self.assertEqual(block.question, "question")
        self.assertEqual(block.ml_nvp, Decimal('1.6'))
        self.assertEqual(block.times_day, 3)
        self.assertEqual(block.weeks, 3)

    def test_edit(self):
        block = DosageActivityFactory()

        data = {'explanation': 'explanation', 'question': 'question',
                'ml_nvp': 1.6, 'times_day': 3, 'weeks': 3}
        block.edit(data, None)
        self.assertEqual(block.explanation, 'explanation')
        self.assertEqual(block.question, "question")
        self.assertEqual(block.ml_nvp, Decimal('1.6'))
        self.assertEqual(block.times_day, 3)
        self.assertEqual(block.weeks, 3)

    def test_unlocked(self):
        user = UserFactory()
        block = DosageActivityFactory()
        self.assertFalse(block.unlocked(user))

        DosageActivityResponse.objects.create(user=user, times_day=1,
                                              weeks=1, ml_nvp=1.1,
                                              dosage_activity=block)
        self.assertTrue(block.unlocked(user))

        block.clear_user_submissions(user)
        self.assertFalse(block.unlocked(user))

    def test_submit(self):
        user = UserFactory()
        block = DosageActivityFactory()
        data = {'mlnvp': 2.1, 'times_day': 1, 'weeks': 6}
        block.submit(user, data)

        resp = DosageActivityResponse.objects.filter(
            user=user, dosage_activity=block).first()
        self.assertEqual(resp.times_day, 1)
        self.assertEqual(resp.ml_nvp, Decimal('2.1'))
        self.assertEqual(resp.weeks, 6)

    def test_as_dict(self):
        block = DosageActivityFactory()
        d = block.as_dict()
        self.assertEqual(block.explanation, d['explanation'])
        self.assertEqual(block.question, d['question'])
        self.assertEqual(block.ml_nvp, Decimal(d['ml_nvp']))
        self.assertEqual(block.times_day, d['times_day'])
        self.assertEqual(block.weeks, d['weeks'])

    def test_json_serialize_round_trip(self):
        block = DosageActivityFactory()
        d1 = block.as_dict()
        serialized = json.dumps(d1)
        d2 = json.loads(serialized)
        self.assertEqual(d1['ml_nvp'], d2['ml_nvp'])

    def test_create_from_dict(self):
        original = DosageActivityFactory()
        duplicate = DosageActivity.create_from_dict(original.as_dict())

        self.assertEqual(original.explanation, duplicate.explanation)
        self.assertEqual(original.question, duplicate.question)
        self.assertEqual(original.ml_nvp, duplicate.ml_nvp)
        self.assertEqual(original.times_day, duplicate.times_day)
        self.assertEqual(original.weeks, duplicate.weeks)


class TestDayAndMonthObjects(TestCase):
    def setUp(self):
        self.m = Month.objects.create(display_name="June")
        self.d = Day.objects.create(calendar=self.m, number=1,
                                    explanation="Your wrong!")

    def test_unicode(self):
        self.assertEqual(str(self.m), "June in None")
        self.assertEqual(str(self.d), "1 Your wrong!")


class TestRetentionRate(TestCase):

    def test_basics(self):
        block = RetentionRateCardFactory()
        HierarchyFactory().get_root().append_pageblock('test', '', block)

        self.assertTrue(smart_str(block).startswith('Root'))
        self.assertIsNotNone(block.pageblock())
        self.assertTrue(block.needs_submit())
        self.assertTrue(block.redirect_to_self_on_submit())

        response = RetentionResponse.objects.create(user=UserFactory(),
                                                    retentionrate=block)
        self.assertTrue(smart_str(response).startswith('Response to Root'))

    def test_retention_click(self):
        retention_click = RetentionClick(click_string="eligible_click")
        self.assertEqual(smart_str(retention_click),
                         "eligible_click")

    def test_unlocked(self):
        user = UserFactory()
        block = RetentionRateCardFactory()
        self.assertFalse(block.unlocked(user))

        response = RetentionResponse.objects.create(user=user,
                                                    retentionrate=block)
        self.assertFalse(block.unlocked(user))

        response.cohort_click = RetentionClickFactory()
        response.save()
        self.assertFalse(block.unlocked(user))

        response.start_date_click = RetentionClickFactory()
        response.save()
        self.assertFalse(block.unlocked(user))

        response.eligible_click = RetentionClickFactory()
        response.save()
        self.assertFalse(block.unlocked(user))

        response.delivery_date_click = RetentionClickFactory()
        response.save()
        self.assertFalse(block.unlocked(user))

        response.follow_up_click = RetentionClickFactory()
        response.save()
        self.assertTrue(block.unlocked(user))

        block.clear_user_submissions(user)
        self.assertFalse(block.unlocked(user))

    def test_add_form(self):
        add_form = RetentionRateCardFactory().add_form()
        self.assertTrue("intro_text" in add_form.fields)

    def test_edit_form(self):
        edit_form = RetentionRateCardFactory().edit_form()
        self.assertTrue("intro_text" in edit_form.fields)

    def test_create(self):
        r = FakeReq()
        r.POST = {'intro_text': 'intro_text info here'}
        block = RetentionRateCard.create(r)
        self.assertEqual(block.intro_text, 'intro_text info here')
        self.assertEqual(block.display_name, "Retention Rate Card")

    def test_edit(self):
        block = RetentionRateCardFactory()
        block.edit({'intro_text': 'updated text'}, None)
        self.assertEqual(block.intro_text, 'updated text')

    def test_as_dict(self):
        block = RetentionRateCardFactory()
        d = block.as_dict()
        self.assertEqual(block.intro_text, d['intro_text'])

    def test_create_from_dict(self):
        d = RetentionRateCardFactory().as_dict()
        block = RetentionRateCard.create_from_dict(d)
        self.assertEqual(d['intro_text'], block.intro_text)


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
        self.assertEqual(str(self.test_conversation), 'G')


class TestCalendarChart(TestCase):

    def test_basics(self):
        block = CalendarChartFactory()
        HierarchyFactory().get_root().append_pageblock('test', '', block)

        self.assertTrue(smart_str(block).startswith('Root'))
        self.assertIsNotNone(block.pageblock())
        self.assertTrue(block.needs_submit())
        self.assertTrue(block.redirect_to_self_on_submit())

    def test_month(self):
        month = MonthFactory()
        self.assertEqual(month.month_name(), 'January')

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

    def test_clear_user_submissions(self):
        user = UserFactory()
        chart = CalendarChartFactory()
        CalendarResponse.objects.create(user=user, calendar_activity=chart)
        chart.clear_user_submissions(user)

        responses = CalendarResponse.objects.filter(
            user=user, calendar_activity=chart)
        self.assertEqual(responses.count(), 0)

    def test_score(self):
        user = UserFactory()
        month = MonthFactory()
        chart = CalendarChartFactory(month=month)

        self.assertEqual(chart.score(user), None)

        resp = CalendarResponse.objects.create(user=user,
                                               calendar_activity=chart)
        self.assertEqual(chart.score(user), None)

        incorrect = Day.objects.create(calendar=month, number=1)
        resp.first_click = incorrect
        resp.save()
        self.assertEqual(chart.score(user), None)

        correct = Day.objects.create(calendar=month, number=4)
        resp.correct_click = correct
        resp.save()
        self.assertEqual(chart.score(user), 0)

        resp.first_click = correct
        resp.save()
        self.assertEqual(chart.score(user), 1)

    def test_add_form(self):
        add_form = CalendarChartFactory().add_form()
        self.assertTrue("correct_date" in add_form.fields)
        self.assertTrue("description" in add_form.fields)
        self.assertTrue("month" in add_form.fields)

    def test_edit_form(self):
        edit_form = CalendarChartFactory().edit_form()
        self.assertTrue("correct_date" in edit_form.fields)
        self.assertTrue("description" in edit_form.fields)
        self.assertTrue("month" in edit_form.fields)

    def test_create(self):
        r = FakeReq()
        month = MonthFactory()
        r.POST = {'description': 'description',
                  'correct_date': 10,
                  'month': month.id}
        block = CalendarChart.create(r)
        self.assertEqual(block.correct_date, 10)
        self.assertEqual(block.description, 'description')
        self.assertEqual(block.month, month)

    def test_edit(self):
        month = MonthFactory()
        block = CalendarChartFactory()
        block.edit({'correct_date': 10,
                    'description': 'updated description',
                    'month': month.id}, None)
        self.assertEqual(block.correct_date, 10)
        self.assertEqual(block.description, 'updated description')
        self.assertEqual(block.month, month)

    def test_as_dict(self):
        day = CorrectDayFactory()
        chart = CalendarChartFactory(month=day.calendar)

        d = chart.as_dict()
        self.assertEqual(chart.description, d['description'])
        self.assertEqual(chart.correct_date, d['correct_date'])
        self.assertEqual(chart.month.display_name, d['month']['display_name'])
        self.assertEqual(1, len(d['month']['days']))
        self.assertEqual(day.number, d['month']['days'][0]['number'])
        self.assertEqual(day.explanation,
                         d['month']['days'][0]['explanation'])

    def test_create_from_dict(self):
        day = CorrectDayFactory()
        original = CalendarChartFactory(month=day.calendar)
        d = original.as_dict()

        duplicate = CalendarChart.create_from_dict(d)
        self.assertEqual(original.description, duplicate.description)
        self.assertEqual(original.correct_date, duplicate.correct_date)
        self.assertEqual(original.month.display_name,
                         duplicate.month.display_name)
        self.assertEqual(duplicate.month.day_set.count(), 1)

        day2 = duplicate.month.day_set.first()
        self.assertEqual(day.number, day2.number)
        self.assertEqual(day.explanation, day2.explanation)


class TestImageInteractive(TestCase):
    def test_basics(self):
        img_int = ImageInteractiveFactory()
        HierarchyFactory().get_root().append_pageblock('test', '', img_int)

        self.assertTrue(smart_str(img_int).startswith('Root'))
        self.assertIsNotNone(img_int.pageblock())

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
        self.assertEqual(img_int.intro_text, 'intro_text info here')
        self.assertEqual(img_int.display_name, "Image Interactive")

    def test_img_int_edit(self):
        img_int = ImageInteractiveFactory()
        img_int.edit({'intro_text': 'updated text'}, None)
        self.assertEqual(img_int.intro_text, 'updated text')

    def test_as_dict(self):
        block = ImageInteractiveFactory()
        d = block.as_dict()
        self.assertEqual(block.intro_text, d['intro_text'])

    def test_create_from_dict(self):
        d = ImageInteractiveFactory().as_dict()
        block = ImageInteractive.create_from_dict(d)
        self.assertEqual(d['intro_text'], block.intro_text)


class TestARTCard(TestCase):
    def test_basics(self):
        artcard = ARTCardFactory()
        HierarchyFactory().get_root().append_pageblock('test', '', artcard)

        self.assertTrue(smart_str(artcard).startswith('Root'))
        self.assertIsNotNone(artcard.pageblock())

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

    def test_artcard_edit(self):
        block = ARTCardFactory()
        block.edit({'intro_text': 'updated text'}, None)
        self.assertEqual(block.intro_text, 'updated text')

    def test_artcard_create(self):
        r = FakeReq()
        r.POST = {'intro_text': 'intro_text info here'}
        artcard = ARTCard.create(r)
        self.assertEqual(artcard.intro_text, 'intro_text info here')
        self.assertEqual(artcard.display_name, "ART Card")

    def test_as_dict(self):
        block = ARTCardFactory()
        d = block.as_dict()
        self.assertEqual(block.intro_text, d['intro_text'])

    def test_create_from_dict(self):
        d = ARTCardFactory().as_dict()
        block = ARTCard.create_from_dict(d)
        self.assertEqual(d['intro_text'], block.intro_text)


class TestAdherenceCard(TestCase):
    def test_basics(self):
        adcard = AdherenceCardFactory()
        HierarchyFactory().get_root().append_pageblock('test', '', adcard)

        self.assertTrue(smart_str(adcard).startswith('Root'))
        self.assertIsNotNone(adcard.pageblock())

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
        r.POST = {'quiz_class': 'quiz class info here'}
        adcard = AdherenceCard.create(r)
        self.assertEqual(adcard.quiz_class, 'quiz class info here')
        self.assertEqual(adcard.display_name, "Adherence Card")

    def test_adcard_edit(self):
        adcard = AdherenceCardFactory()
        adcard.edit({'quiz_class': 'updated class'}, None)
        self.assertEqual(adcard.quiz_class, 'updated class')

    def test_as_dict(self):
        block = AdherenceCardFactory()
        d = block.as_dict()
        self.assertEqual(block.quiz_class, d['quiz_class'])

    def test_create_from_dict(self):
        d = AdherenceCardFactory().as_dict()
        block = AdherenceCard.create_from_dict(d)
        self.assertEqual(d['quiz_class'], block.quiz_class)
