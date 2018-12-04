from json import loads
import json

from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory
from django.test.client import Client
from pagetree.models import Hierarchy, UserPageVisit
from pagetree.tests.factories import ModuleFactory

from nepi.activities.models import ConversationResponse, RetentionResponse, \
    CalendarResponse
from nepi.activities.tests.factories import ConversationScenarioFactory, \
    RetentionRateCardFactory, CalendarChartFactory, IncorrectDayOneFactory, \
    IncorrectDayTwoFactory, CorrectDayFactory, GoodConversationFactory
from nepi.activities.views import UpdateConversationView
from nepi.main.tests.factories import UserProfileFactory


class TestLastResponseSaveViews(TestCase):
    '''Going through scenario of admin goes to admin panel:
        1. admin creates conversation pageblock.
        2. admin then decides to update the conversation information
        3. admin then adds conversations to the conversation scenario
        4. admin then edits the conversations
    '''
    def setUp(self):
        ModuleFactory("optionb-en", "/pages/optionb/en/")
        self.hierarchy = Hierarchy.objects.get(name='optionb-en')
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
        self.assertEqual(upv.status, "incomplete")

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
        self.assertEqual(upv.status, "complete")


class TestRetentionResponseView(TestCase):

    def setUp(self):
        ModuleFactory("optionb-en", "/pages/optionb/en/")
        hierarchy = Hierarchy.objects.get(name='optionb-en')
        self.section = hierarchy.get_root().get_first_leaf()

        self.rf = RetentionRateCardFactory()
        self.section.append_pageblock(label="Retention Card", css_extra='',
                                      content_object=self.rf)

        self.user = UserProfileFactory().user
        self.url = reverse('retention_click')

    def test_retention_response(self):
        self.client.login(username=self.user.username, password="test")

        '''Make sure RetentionResponse returns correctly'''
        response = self.client.post(
            self.url,
            data={'click_string': "cohort_click",
                  'retention_id': self.rf.pk}
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, RetentionResponse.objects.filter(
            retentionrate=self.rf, user=self.user).count())
        the_json = json.loads(response.content)
        self.assertEqual(the_json, {'done': False, 'success': True})

        '''See what happens with unacceptable click'''
        response = self.client.post(
            "/activities/retention_click/",
            data={'click_string': "weirdness_here",
                  'retention_id': self.rf.pk}
            )
        self.assertEqual(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEqual(the_json, {'success': False})

        '''This is to check that ajax returns true if
        user clicks on the same thing twice'''
        response = self.client.post(
            "/activities/retention_click/",
            data={'click_string': "cohort_click",
                  'retention_id': self.rf.pk}
            )
        self.assertEqual(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEqual(the_json, {'done': False, 'success': True})

        '''We should also check that the page still needs to be submitted'''
        self.assertTrue(self.rf.needs_submit())

    def test_retention_response_save_clicks(self):
        self.client.login(username=self.user.username, password="test")

        self.assertFalse(self.rf.unlocked(self.user))

        data = {'retention_id': self.rf.pk, 'click_string': 'cohort_click'}
        response = self.client.post(self.url, data)
        the_json = loads(response.content)
        self.assertFalse(the_json['done'])
        self.assertTrue(the_json['success'])
        self.assertEqual(0, UserPageVisit.objects.filter(
            user=self.user, section=self.section).count())

        data['click_string'] = 'start_date_click'
        self.client.post(self.url, data)

        data['click_string'] = 'eligible_click'
        self.client.post(self.url, data)

        data['click_string'] = 'delivery_date_click'
        self.client.post(self.url, data)

        data['click_string'] = 'follow_up_click'
        response = self.client.post(self.url, data)
        the_json = loads(response.content)
        self.assertTrue(the_json['done'])

        self.assertTrue(self.rf.unlocked(self.user))

        upv = UserPageVisit.objects.get(user=self.user, section=self.section)
        self.assertEqual(upv.status, 'complete')

    def test_retention_response_duplicate(self):
        self.client.login(username=self.user.username, password="test")

        # create multiple retention responses
        RetentionResponse.objects.create(user=self.user, retentionrate=self.rf)
        RetentionResponse.objects.create(user=self.user, retentionrate=self.rf)

        '''Make sure RetentionResponse returns correctly'''
        response = self.client.post(
            self.url,
            data={'click_string': "cohort_click",
                  'retention_id': self.rf.pk}
            )
        self.assertEqual(response.status_code, 200)


class TestCalendarResponseView(TestCase):

    def setUp(self):
        ModuleFactory("optionb-en", "/pages/optionb/en/")
        self.hierarchy = Hierarchy.objects.get(name='optionb-en')
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
        self.assertEqual(upv.status, "incomplete")

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
        self.assertEqual(upv.status, "complete")


class TestUpdateConversationView(TestCase):

    def test_get(self):
        conversation = GoodConversationFactory()
        url = reverse('update_conversation', kwargs={'pk': conversation.id})

        up = UserProfileFactory()
        self.client.login(username=up.user.username, password="test")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_context_data(self):
        conversation = GoodConversationFactory()
        url = reverse('update_conversation', kwargs={'pk': conversation.id})

        view = UpdateConversationView()
        view.object = conversation
        view.request = RequestFactory().post(url)

        ctx = view.get_context_data()
        self.assertEqual(ctx['scenario'], view.object.get_scenario())
