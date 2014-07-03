from django.test import TestCase, RequestFactory
from django.test.client import Client
from nepi.activities.models import ConversationScenario, ConversationResponse
from nepi.activities.views import SaveResponse, LastResponse
from nepi.main.tests.factories import UserFactory, \
    HierarchyFactory, UserProfileFactory
from nepi.activities.test.factories import ConversationPageblockHierarchyFactory, ConversationScenarioFactory
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
        self.user = UserFactory(is_superuser=True)
        self.up = UserProfileFactory(user=self.user)
        self.user.set_password("test")
        self.user.save()
        self.client = Client()
        self.client.login(username=self.user.username, password="test")
        self.factory = RequestFactory()

    def test_edit_conversation_page_form(self):
        r = self.client.get("/pages/%s/edit/%s/" %
                            (self.hierarchy.name, self.section.slug))
        request = self.factory.post(
            "/pages/%s/edit/%s/" % (self.hierarchy.name, self.section.slug),
            {"label": "conversation label",
             "description": "conversation description"})
        request.user = self.user
        conversation = ConversationScenario.create(request)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(conversation.needs_submit())
        self.assertFalse(conversation.unlocked(request.user))

#     def test_getting_scenario_via_get(self):
#         '''this isn't actually testing for a conversation scenario pageblock'''
#         hierarchy = ConversationPageblockHierarchyFactory()
#         section = self.hierarchy.get_root().get_first_leaf()
#         user = UserFactory(is_superuser=True)
#         user.set_password("test")
#         up = UserProfileFactory(user=self.user)
#         client = Client()
#         self.client.login(username=user.username, password="test")
#         request = self.client.get(
#             "/pages/%s/%s/" % (hierarchy.name, section.slug))
#         self.assertEqual(request.status_code, 200)

    def test_save_resposne_and_last_response_via_post(self):
        cs = ConversationScenarioFactory()
        cs.save()  # do I need this?
        user = UserFactory(is_superuser=True)
        user.set_password("test")
        user.save()
        up = UserProfileFactory(user=self.user)
        up.save()
        client = Client()
        client.login(username=user.username, password="test")
        
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


        request = self.client.post(
            "/get_click/",
            data={'scenario': cs.pk,
                  'conversation': cs.good_conversation.pk},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
        response = SaveResponse.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ConversationResponse.objects.count())
        self.assertTrue(ConversationResponse.objects.filter(conv_scen=cs,
                                                            user=user))
        '''Make sure there is one click object for the resposne and click two
        and three are None.'''
        cr = ConversationResponse.objects.filter(conv_scen=cs, user=user)
        self.assertNotNone(cr.first_click)
        self.assertNone(cr.second_click)
        self.assertNone(cr.third_click)
        
        '''Now check that get last response works'''
        request = self.client.post(
            "/get_last/", data={ 'scenario': cs.pk}
            )
        response = LastResponse.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response, {'success': True, 'last_conv': cresp.first_click})

        '''Testing second click through POST method'''
        request = self.client.post(
            "/get_click/", data={'scenario': cs.pk,
                                 'conversation': cs.bad_conversation.pk}
            )
        response = SaveResponse.as_view()(request)
        self.assertEqual(response.status_code, 200)
        cr = ConversationResponse.objects.filter(conv_scen=cs, user=user)
        self.assertNotNone(cr.first_click)
        self.assertNotNone(cr.second_click)
        self.assertNone(cr.third_click)
        
        '''Check last response'''
        request = self.client.post(
            "/get_last/", data={ 'scenario': cs.pk}
            )
        response = LastResponse.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response, {'success': True,
                                    'last_conv': cr.second_click})

        '''Testing third click through POST method'''
        request = self.client.post(
            "/get_click/", data={'scenario': cs.pk,
                                 'conversation': cs.bad_conversation.pk
            })
        response = SaveResponse.as_view()(request)
        self.assertEqual(response.status_code, 200)
        cr = ConversationResponse.objects.filter(conv_scen=cs, user=user)
        self.assertNotNone(cr.first_click)
        self.assertNotNone(cr.second_click)
        self.assertNotNone(cr.third_click)

        request = self.client.post(
            "/get_last/", data={ 'scenario': cs.pk}
            )
        response = LastResponse.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response, {'success': True,
                                    'last_conv': cr.third_click})



# ##        post_data = { 
#     "jsonrpc" : "2.0", "method": method, "params" : params, "id" : id }
# return client.post('/api/json/', 
#                     json.dumps(post_data), "text/json",            
#                     )



# 
#  162         response = self.client.post('/accounts/login/',
# 163                                     {'username': self.user.username,
# 164                                      'password': 'test'},
# 165                                     HTTP_X_REQUESTED_WITH='XMLHttpRequest')
# 166         self.assertEquals(response.status_code, 200)
# 167         the_json = json.loads(response.content)
# 168         self.assertTrue(the_json['next'], "/")
# 169         self.assertTrue('error' not in the_json)
# 170
# 171     def test_login_participant(self):
# 172         # participants cannot login through the /accounts/login mechanism
# 173         # as the backend authenticators kick out inactive Users
# 174         pwd = generate_password(self.participant.username)
# 175         response = self.client.post('/accounts/login/',
# 176                                     {'username': self.participant.username,
# 177                                      'password': pwd},
# 178                                     HTTP_X_REQUESTED_WITH='XMLHttpRequest')
# 179         self.assertEquals(response.status_code, 200)
# 180         the_json = json.loads(response.content)
# 181         self.assertTrue(the_json['error'], True)







#             return render_to_json_response()
# 
# 
# post_data = { 
#     "jsonrpc" : "2.0", "method": method, "params" : params, "id" : id }
# return client.post('/api/json/', 
#                     json.dumps(post_data), "text/json",            
#                     HTTP_X_REQUESTED_WITH='XMLHttpRequest')




# 
#         self.client = Client()
#         self.client.login(username=self.user.username, password="test")
#         self.factory = RequestFactory()
# 
# class SaveResponse(View, JSONResponseMixin):
#     def post(self, request):
#         scenario = get_object_or_404(ConversationScenario,
#                                      pk=request.POST['scenario'])
#         conversation = get_object_or_404(Conversation,
#                                          pk=request.POST['conversation'])
#         conclick = ConvClick.objects.create(conversation=conversation)
#         conclick.save()
#         current_user = User.objects.get(pk=request.user.pk)
#         rs, created = ConversationResponse.objects.get_or_create(
#             conv_scen=scenario, user=current_user)
#         if rs.first_click is None:
#             rs.first_click = conclick
#             rs.save()
#         elif rs.first_click is not None and rs.second_click is None:
#             rs.second_click = conclick
#             rs.third_click = conclick
#             rs.save()
#         elif rs.second_click is not None:
#             rs.third_click = conclick
#             rs.save()
#         return render_to_json_response({'success': True})
# 
# 
# class LastResponse(View, JSONResponseMixin):
#     '''Should this be a create view?'''
#     def post(request):
#         scenario = get_object_or_404(ConversationScenario,
#                                      pk=request.POST['scenario'])
#         user = User.objects.get(pk=request.user.pk)
#         try:
#             cresp = ConversationResponse.objects.get(
#                 user=user, scenario=scenario)
#             if cresp.third_click is not None:
#                 return render_to_json_response(
#                     {'success': True, 'last_conv': cresp.third_click})
#             elif (cresp.first_click is not None
#                   and cresp.second_click is None):
#                     return render_to_json_response(
#                         {'success': True, 'last_conv': cresp.first_click})
# 
#         except ConversationResponse.DoesNotExist:
#             return render_to_json_response({'success': False})