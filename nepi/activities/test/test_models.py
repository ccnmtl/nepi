from datetime import datetime
from django.contrib.auth.models import User
from pagetree.models import Hierarchy
from factories import UserFactory, ConversationScenarioFactory
from factories import ConversationScenarioFactory
from factories import ConversationFactory
from factories import ConversationResponseFactory #, HierarchyFactory
from django.test import TestCase


class TestConversationScenario(TestCase):
    def test_unicode(self):
        cs = ConversationScenarioFactory()
        # possibilities for submissions
        # it is first user submission - no
        # conversation response has been created yet
        
        #submit
        # user has clicked on one conversation and clicks on same one
        # user has clicked on both conversations
        # user 
        # self.assertEqual(str(cs), "Conversation Scenario")

    def test_first_submission(self):
        # on first user submission - no
        # conversation response has been created yet
        cs = ConversationScenarioFactory()
        user = UserFactory()
        cr = ConversationResponseFactory()
        #cs.submit(user, cr)
        #cr = ConversationResponseFactory()
        #cr.scenario = cs
        #cr.user = user
        #cr.save()
        
#    conv_scen = models.ForeignKey(ConversationScenario, null=True, blank=True)
#    user = models.ForeignKey(User)
#    first_click = models.ForeignKey(ConvClick, related_name="first_click", null=True, blank=True)
#    second_click = models.ForeignKey(ConvClick, related_name="second_click", null=True, blank=True)
#    last_click = models.ForeignKey(ConvClick, related_name="third_click", null=True, blank=True)

class TestConversation(TestCase):
    def test_unicode(self):
        pass
        #c = ConversationFactory()
        #self.assertEqual(str(c), "Conversation Scenario")
#class PatientConversationFactory(factory.DjangoModelFactory):
#    FACTORY_FOR = PatientConversation
#    starting = ""
#    response_one = "Patient thought can go here"
#    response_two = "Patient response can go here"

#class ConversationDialogFactory(factory.DjangoModelFactory):
#    FACTORY_FOR = ConversationDialog
#    order = 1
#    content = "This is the nurse's first line"
