from datetime import datetime
from django.contrib.auth.models import User
from pagetree.models import Hierarchy
from .factories import UserFactory, ConversationScenarioFactory, \
    ConversationFactory


#class PatientConversationFactory(factory.DjangoModelFactory):
#    FACTORY_FOR = PatientConversation
#    starting = ""
#    response_one = "Patient thought can go here"
#    response_two = "Patient response can go here"

#class ConversationDialogFactory(factory.DjangoModelFactory):
#    FACTORY_FOR = ConversationDialog
#    order = 1
#    content = "This is the nurse's first line"
