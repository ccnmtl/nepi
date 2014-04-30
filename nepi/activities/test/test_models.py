from datetime import datetime
from django.contrib.auth.models import User
from pagetree.models import Hierarchy
from factories import UserFactory, ConversationScenarioFactory
from factories import ConversationScenarioFactory
from factories import ConversationFactory #, HierarchyFactory
from django.test import TestCase


class TestConversationScenario(TestCase):
    def test_unicode(self):
        pass
        #cs = ConversationScenarioFactory()
        #self.assertEqual(str(cs), "Conversation Scenario")


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
