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
        '''Test second click'''
        cr.second_click = click_two
        cr.save()
        self.assertEquals(click_two.conversation.scenario_type,
                          cr.second_click.conversation.scenario_type)
        self.assertIsNone(cr.third_click)
        self.assertTrue(scenario.unlocked(user))
        self.assertTrue(scenario.needs_submit())
        '''Test third click'''
        cr.third_click=click_three
        cr.save()
        self.assertEquals(click_three.conversation.scenario_type,
                          cr.third_click.conversation.scenario_type)
        self.assertIsNotNone(cr.third_click)
        self.assertTrue(scenario.unlocked(user))



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


