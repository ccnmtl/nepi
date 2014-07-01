from django.test import TestCase, RequestFactory
from django.test.client import Client
from nepi.activities.models import ConversationScenario, ConversationResponse
from nepi.activities.views import SaveResponse, LastResponse
from nepi.main.tests.factories import UserFactory, \
    HierarchyFactory, UserProfileFactory
from nepi.activities.test.factories import GoodConversationFactory, ConversationScenarioFactory, ConversationResponseFactory


'''make sure logged in super user can
create conversation scenario pageblocks'''


class TestLoggedInViews(TestCase):
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


#     def test_post_save_response_view_test_client(self):
#         scenario = ConversationScenarioFactory()
#         conversation = GoodConversationFactory()
#         cr = ConversationResponseFactory()
#         url = reverse('save-response', kwargs={"scenario": scenario,
#              "conversation": conversation})
#         r = self.client.post(url)
#         self.assertEqual(r.status_code, 200)
#         # self.assertTemplateUsed(response, 'hello-world.txt')

    def test_details(self):
        scenario = ConversationScenarioFactory()
        conversation = GoodConversationFactory()
        request = self.factory.post('/get_click/')
        request.POST = {"scenario": scenario, "conversation": conversation}
        request.user = self.user
        # Test my_view() as if it were deployed at /customer/details
        # view = LastResponse.post()
        response = LastResponse.post(request)
        # self.assertEqual(response.status_code, 200)

#     def test_post_save_response_view_request_factory(self):
#         scenario = ConversationScenarioFactory()
#         conversation = GoodConversationFactory()
#         request = self.factory.post(
#             "/get_click/",
#             {"scenario": scenario,
#              "conversation": conversation})
#         request.user = self.user
#         #response = ConversationResponse.objects.create(request)
#         self.assertEqual(response.status_code, 200)
#         #self.assertTrue(response.needs_submit())
#         #self.assertFalse(response.unlocked(request.user))
# 
#         def test_get(self):
#             SomeModel.objects.create(slug=u'world')
#             view = HelloView.as_view()
#             response = view(slug=u'world')
#             self.assertEqual(response.status_code, 200)
#             self.assertTemplateUsed(response, 'hello-world.txt')


#              def test_get(self):
#             SomeModel.objects.create(slug=u'world')
#             url = reverse('hello', kwargs={'slug': u'world'})
#             response = self.client.get(url)
#             self.assertEqual(response.status_code, 200)
#             self.assertTemplateUsed(response, 'hello-world.txt'
# #         scenario = get_object_or_404(ConversationScenario,
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