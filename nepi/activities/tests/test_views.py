from django.test import TestCase, RequestFactory
from django.test.client import Client
from nepi.activities.models import ConversationResponse
from nepi.main.tests.factories import HierarchyFactory, UserProfileFactory
from nepi.activities.tests.factories import ConversationScenarioFactory
import json


class TestActivityViews(TestCase):
    '''Going through scenario of admin goes to admin panel:
        1. admin creates conversation pageblock.
        2. admin then decides to update the conversation information
        3. admin then adds conversations to the conversation scenario
        4. admin then edits the conversations
    '''
    def setUp(self):
        self.hierarchy = HierarchyFactory()
        self.section = self.hierarchy.get_root().get_first_leaf()
        self.factory = RequestFactory()

    def test_save_response_and_last_response_via_post(self):
        cs = ConversationScenarioFactory()
        up = UserProfileFactory()
        client = Client()
        self.assertTrue(client.login(username=up.user.username,
                                     password="test"))
        '''Make sure LastResposne returns correctly'''
#         request = self.client.post(
#             "/get_last/", data={ 'scenario': cs.pk},
#             HTTP_X_REQUESTED_WITH='XMLHttpRequest'
#             )
#         response = LastResponse.as_view()(request)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response, {'success': False})
#         # the above worked now trying other way below
#         the_json = json.loads(response.content)
#         self.assertTrue(the_json['success'], Flase)

        response = client.post(
            "/activities/get_click/",
            data={'scenario': cs.pk,
                  'conversation': cs.good_conversation.pk}
            )
        # this is for use with request factory
        # response = SaveResponse.as_view()(request)
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

        '''Now check that get last response works'''
        response = client.post(
            "/activities/get_last/", data={'scenario': cs.pk}
            )
        # response = LastResponse.as_view()(request)
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
        # response = SaveResponse.as_view()(request)
        self.assertEqual(response.status_code, 200)
        cr = ConversationResponse.objects.get(conv_scen=cs, user=up.user)
        self.assertIsNotNone(cr.first_click)
        self.assertIsNotNone(cr.second_click)
        self.assertIsNotNone(cr.third_click)

        '''Check last response'''
        response = client.post(
            "/activities/get_last/", data={'scenario': cs.pk}
            )
        # response = LastResponse.as_view()(request)
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
        # response = SaveResponse.as_view()(request)
        self.assertEqual(response.status_code, 200)
        cr = ConversationResponse.objects.get(conv_scen=cs, user=up.user)
        self.assertIsNotNone(cr.first_click)
        self.assertIsNotNone(cr.second_click)
        self.assertIsNotNone(cr.third_click)

        response = client.post(
            "/activities/get_last/", data={'scenario': cs.pk}
            )
        # response = LastResponse.as_view()(request)
        self.assertEqual(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertEqual(the_json, {'success': True,
                                    'last_conv':
                                    cr.third_click.conversation.scenario_type
                                    })
