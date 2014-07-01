from factories import UserFactory, ConversationScenarioFactory, \
    ConvClickFactory
from django.test import TestCase
from nepi.activities.models import ConversationResponse


class TestConversationScenario(TestCase):
    '''We want to make sure we can create a conversation
     response associated with the user upon submission.'''

    def test_first_click(self):
        '''testing first click of response object'''
        user = UserFactory()
        scenario = ConversationScenarioFactory()
        first_click = ConvClickFactory()
        response = ConversationResponse.objects.create(
            conv_scen=scenario, user=user, first_click=first_click)
        response.save()
        self.assertIn(response, user.conversationresponse_set.all())
        self.assertEqual(response.first_click, first_click)

    def test_second_click(self):
        '''testing second click of response object'''
        user = UserFactory()
        scenario = ConversationScenarioFactory()
        click_one = ConvClickFactory()
        click_two = ConvClickFactory()
        response = ConversationResponse.objects.create(
            conv_scen=scenario, user=user,
            first_click=click_one, second_click=click_two)
        response.save()
        self.assertIn(response, user.conversationresponse_set.all())
        self.assertEqual(response.first_click, click_one)
        self.assertEqual(response.second_click, click_two)



#     def last_response(self, user):
#         try:
#             response = ConversationResponse.objects.get(
#                 conv_scen=self, user=user)
#             if (response.first_click is not None
#                     and response.second_click is not None):
#                 return response.third_click.conversation.scenario_type
#             elif (response.first_click is not None
#                     and response.second_click is None):
#                 return response.first_click.conversation.scenario_type
#         except ConversationResponse.DoesNotExist:
#             return 0

    def test_last_response(self):
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
        test_first = ConversationResponse.objects.create(conv_scen=scenario,
                                                               user=user,
                                                               first_click=click_one)
        self.assertEquals(click_one.conversation.scenario_type,
                          test_first.first_click.conversation.scenario_type)
        self.assertIsNone(test_first.second_click)
        test_second = ConversationResponse.objects.create(conv_scen=scenario,
                                                                   user=user,
                                                                   first_click=click_one,
                                                                   second_click=click_two)
        self.assertEquals(click_two.conversation.scenario_type,
                          test_second.second_click.conversation.scenario_type)
        self.assertIsNone(test_second.third_click)
        test_third = ConversationResponse.objects.create(conv_scen=scenario,
                                                                   user=user,
                                                                   first_click=click_one,
                                                                   second_click=click_two,
                                                                   third_click=click_three)
        self.assertEquals(click_three.conversation.scenario_type,
                          test_third.third_click.conversation.scenario_type)
        self.assertIsNotNone(test_third.third_click)



# class ConversationScenario(models.Model):
#     pageblocks = generic.GenericRelation(PageBlock)
#     description = models.TextField(blank=True)
#     display_name = "Conversation Scenario"
#     template_file = "activities/conversation.html"
#     js_template_file = "activities/conversation_js.html"
#     css_template_file = "activities/conversation_css.html"
#     exportable = False
#     importable = False
#     good_conversation = models.ForeignKey(Conversation, null=True, blank=True,
#                                           related_name='good_conversation')
#     bad_conversation = models.ForeignKey(Conversation, null=True, blank=True,
#                                          related_name='bad_conversation')
# 
#     def pageblock(self):
#         return self.pageblocks.all()[0]
# 
#     def __unicode__(self):
#         return unicode(self.pageblock())
# 
#     def needs_submit(self):
#         '''Pageblock will see that block has needs
#         submit and then check the conditions defined
#         in "unlocked to determine if it is unlocked or not."'''
#         return True
# 
#     @classmethod
#     def add_form(self):
#         return ConversationScenarioForm()
# 
#     def edit_form(self):
#         if self.good_conversation is None and self.bad_conversation is None:
#             class EditForm(forms.Form):
#                 alt_text = ("<a href=\"" +
#                             reverse("create_conversation", args=[self.id])
#                             + "\">add a conversation</a>")
#                 description = forms.CharField(initial=self.description)
#             form = EditForm()
#             return form
#         elif (self.good_conversation is not None
#               and self.bad_conversation is None):
#                 class EditForm(forms.Form):
#                     alt_text = ("<a href=\"" +
#                                 reverse("create_conversation", args=[self.id])
#                                 + "\">add a bad conversation</a><br>" +
#                                 "<a href=\"" +
#                                 reverse("update_conversation",
#                                         args=[self.good_conversation.id])
#                                 + "\">update good conversation</a>")
#                     description = forms.CharField(initial=self.description)
#                 form = EditForm()
#                 return form
#         elif (self.good_conversation is None
#               and self.bad_conversation is not None):
#                 class EditForm(forms.Form):
#                     alt_text = ("<a href=\"" +
#                                 reverse("create_conversation", args=[self.id])
#                                 + "\">add a good conversation</a><br>" +
#                                 "<a href=\"" +
#                                 reverse("update_conversation",
#                                         args=[self.bad_conversation.id])
#                                 + "\">update bad conversation</a>")
#                     description = forms.CharField(initial=self.description)
#                 form = EditForm()
#                 return form
#         elif (self.good_conversation is not None
#               and self.bad_conversation is not None):
#                 class EditForm(forms.Form):
#                     alt_text = ("<a href=\"" +
#                                 reverse("update_conversation",
#                                         args=[self.good_conversation.id])
#                                 + "\">update a good conversation</a><br>" +
#                                 "<a href=\"" +
#                                 reverse("update_conversation",
#                                         args=[self.bad_conversation.id])
#                                 + "\">update bad conversation</a>")
#                     description = forms.CharField(initial=self.description)
#                 form = EditForm()
#                 return form
# 
#     @classmethod
#     def create(self, request):
#         form = ConversationScenarioForm(request.POST)
#         return form.save()
# 
#     def edit(self, vals, files):
#         form = ConversationScenarioForm(data=vals, files=files, instance=self)
#         if form.is_valid():
#             form.save()
# 
#     def redirect_to_self_on_submit(self):
#         '''Show student feedback before proceeding,
#         not sure if this is ever called since there is no "submit"'''
#         return True
# 
#     def unlocked(self, user):
#         '''We want to make sure the user has selected both dialogs
#            from the conversation before they can proceed.'''
#         response = ConversationResponse.objects.filter(
#             conv_scen=self, user=user)
#         if (len(response) == 1
#                 and response[0].first_click is not None
#                 and response[0].second_click is not None):
#             return True
#         else:
#             return False
# 

