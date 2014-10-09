import json

from django.test import TestCase, RequestFactory
from django.test.client import Client
from pagetree.models import Hierarchy, UserPageVisit
from pagetree.tests.factories import ModuleFactory

from nepi.activities.models import ConversationResponse, RetentionResponse, \
    CalendarResponse
from nepi.activities.tests.factories import ConversationScenarioFactory, \
    RetentionRateCardFactory, CalendarChartFactory, IncorrectDayOneFactory, \
    IncorrectDayTwoFactory, CorrectDayFactory
from nepi.main.tests.factories import UserProfileFactory


class TestLastResponseSaveViews(TestCase):
    '''Going through scenario of admin goes to admin panel:
        1. admin creates conversation pageblock.
        2. admin then decides to update the conversation information
        3. admin then adds conversations to the conversation scenario
        4. admin then edits the conversations
    '''
    def setUp(self):
        ModuleFactory("main", "/pages/main/")
        self.hierarchy = Hierarchy.objects.get(name='main')
        self.section = self.hierarchy.get_root().get_first_leaf()
        self.factory = RequestFactory()

    def test_save_response_and_last_response_via_post(self):
        cs = ConversationScenarioFactory()

        up = UserProfileFactory()
        client = Client()
        self.assertTrue(client.login(username=up.user.username,
                                     password="test"))

        self.section.append_pageblock(label="Conversation Scenario",
                                      css_extra='',
                                      content_object=cs)
        UserPageVisit.objects.create(user=up.user, section=self.section)

        '''Make sure LastResponse returns correctly'''

        response = client.post(
            "/activities/get_click/",
            data={'scenario': cs.pk,
                  'conversation': cs.good_conversation.pk}
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, ConversationResponse.objects.count())
        self.assertTrue(ConversationResponse.objects.filter(conv_scen=cs,
                                                            user=up.user))
        '''Make sure there is one click object for the resposne and click two
        and three are None.'''
        cr = ConversationResponse.objects.get(conv_scen=cs, user=up.user)
        self.assertIsNotNone(cr.first_click)
        self.assertIsNone(cr.second_click)
        self.assertIsNone(cr.third_click)

        upv = UserPageVisit.objects.get(user=up.user, section=self.section)
        self.assertEquals(upv.status, "incomplete")

        '''Now check that get last response works'''
        response = client.post(
            "/activities/get_last/", data={'scenario': cs.pk}
            )

        self.assertEqual(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEqual(the_json, {'success': True,
                                    'last_conv':
                                    cr.first_click.conversation.scenario_type
                                    })

        '''Testing second click through POST method'''
        response = client.post(
            "/activities/get_click/", data={'scenario': cs.pk,
                                            'conversation':
                                            cs.bad_conversation.pk}
            )

        self.assertEqual(response.status_code, 200)
        cr = ConversationResponse.objects.get(conv_scen=cs, user=up.user)
        self.assertIsNotNone(cr.first_click)
        self.assertIsNotNone(cr.second_click)
        self.assertIsNotNone(cr.third_click)

        '''Check last response'''
        response = client.post(
            "/activities/get_last/", data={'scenario': cs.pk}
            )
        self.assertEqual(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEqual(the_json, {'success': True,
                                    'last_conv':
                                    cr.second_click.conversation.scenario_type
                                    })

        '''Testing third click through POST method'''
        response = client.post(
            "/activities/get_click/", data={'scenario': cs.pk,
                                            'conversation':
                                            cs.bad_conversation.pk
                                            })
        self.assertEqual(response.status_code, 200)
        cr = ConversationResponse.objects.get(conv_scen=cs, user=up.user)
        self.assertIsNotNone(cr.first_click)
        self.assertIsNotNone(cr.second_click)
        self.assertIsNotNone(cr.third_click)

        response = client.post(
            "/activities/get_last/", data={'scenario': cs.pk}
            )
        self.assertEqual(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEqual(the_json, {'success': True,
                                    'last_conv':
                                    cr.third_click.conversation.scenario_type
                                    })

        upv = UserPageVisit.objects.get(user=up.user, section=self.section)
        self.assertEquals(upv.status, "complete")


class TestRetentionResponseView(TestCase):

    def test_retention_response(self):
        rf = RetentionRateCardFactory()
        up = UserProfileFactory()
        client = Client()
        self.assertTrue(client.login(username=up.user.username,
                                     password="test"))
        '''Make sure RetentionResponse returns correctly'''
        response = client.post(
            "/activities/retention_click/",
            data={'click_string': "cohort_click",
                  'retention_id': rf.pk}
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, RetentionResponse.objects.count())
        self.assertTrue(RetentionResponse.objects.filter(retentionrate=rf,
                                                         user=up.user))
        the_json = json.loads(response.content)
        self.assertEqual(the_json, {'done': False, 'success': True})

        '''See what happens with unacceptable click'''
        response = client.post(
            "/activities/retention_click/",
            data={'click_string': "weirdness_here",
                  'retention_id': rf.pk}
            )
        self.assertEqual(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEqual(the_json, {'success': False})

        '''This is to check that ajax returns true if
        user clicks on the same thing twice'''
        response = client.post(
            "/activities/retention_click/",
            data={'click_string': "cohort_click",
                  'retention_id': rf.pk}
            )
        self.assertEqual(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEqual(the_json, {'done': False, 'success': True})

        '''Test that it is storing the submitted
        click string values'''
        self.value = RetentionResponse.objects.filter(retentionrate=rf,
                                                      user=up.user)
        # self.assertIsNotNone(self.value[0].cohort_click)
        # self.assertIsNotNone(self.value[0].jan_click)
        '''We should also check that the page still needs to be submitted'''
        self.assertTrue(rf.needs_submit())


class TestCalendarResponseView(TestCase):

    def setUp(self):
        ModuleFactory("main", "/pages/main/")
        self.hierarchy = Hierarchy.objects.get(name='main')
        self.section = self.hierarchy.get_root().get_first_leaf()

    def test_calendar_response(self):
        cal_chart = CalendarChartFactory()
        inc_day_1 = IncorrectDayOneFactory()
        inc_day_2 = IncorrectDayTwoFactory()
        correct_day = CorrectDayFactory()
        up = UserProfileFactory()
        client = Client()
        self.assertTrue(client.login(username=up.user.username,
                                     password="test"))

        self.section.append_pageblock(label="Calendar View",
                                      css_extra='',
                                      content_object=cal_chart)
        UserPageVisit.objects.create(user=up.user, section=self.section)

        '''Make sure SaveCalendarResponse returns correctly'''
        response = client.post(
            "/activities/calendar_click/",
            data={'day': inc_day_1.pk,
                  'calendar': cal_chart.pk}
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, CalendarResponse.objects.count())
        self.assertTrue(CalendarResponse.objects.filter(
            calendar_activity=cal_chart, user=up.user))
        the_json = json.loads(response.content)
        self.assertEqual(the_json, {'success': True})

        upv = UserPageVisit.objects.get(user=up.user, section=self.section)
        self.assertEquals(upv.status, "incomplete")

        '''Make sure it still needs to be submitted since we
        only have one user response'''
        self.assertTrue(cal_chart.needs_submit())

        '''See what happens with a second unacceptable click'''
        response = client.post(
            "/activities/calendar_click/",
            data={'day': inc_day_2.pk,
                  'calendar': cal_chart.pk}
            )
        self.assertEqual(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEqual(the_json, {'success': True})

        '''Make sure it still needs to be submitted and doesn't
        count second wrong click as correct answer'''
        self.assertTrue(cal_chart.needs_submit())

        '''Make sure correct click is stored and block
        no longer needs to be submitted'''
        response = client.post(
            "/activities/calendar_click/",
            data={'day': correct_day.pk,
                  'calendar': cal_chart.pk}
            )
        self.assertEqual(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEqual(the_json, {'success': True})

        upv = UserPageVisit.objects.get(user=up.user, section=self.section)
        self.assertEquals(upv.status, "complete")
