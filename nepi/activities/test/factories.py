from datetime import datetime
from django.contrib.auth.models import User
from activities.models import NurseConversation
from activities.models import PatientConversation
from activities.models import ConversationDialog
from pagetree.models import Hierarchy
import factory


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: "user%d" % n)

class NurseConversationFactory(factory.DjangoModelFactory):
    FACTORY_FOR = NurseConversation
    starting = "Asking patient appropriate question part one"
    response_one = ""
    response_two = ""

class PatientConversationFactory(factory.DjangoModelFactory):
    FACTORY_FOR = PatientConversation
    starting = ""
    response_one = "Patient thought can go here"
    response_two = "Patient response can go here"

class ConversationDialogFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ConversationDialog
    order = 1
    content = "This is the nurse's first line"


