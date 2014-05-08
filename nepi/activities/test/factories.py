from django.contrib.auth.models import User
import factory
from nepi.activities.models import ConversationScenario, \
    Conversation, ConversationResponse, ConvClick
from datetime import datetime

class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: "user%d" % n)


class ConversationScenarioFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ConversationScenario
    description = "Description for the Conversation Scenario"


class ConversationFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Conversation
    text_one = "We assume text one is the starting text"
    text_two = "Text 2 is the response to whatever the other party says"
    text_three = "Text 3 is an optional response/thought to " + \
        "whatever the other party says"
    complete_dialog = "This is the entire Nurse/Patient exchange" + \
        " that is displayed when the user selects the starting text"


class ConversationResponseFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ConversationResponse


class ConvClickFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ConvClick
    created = datetime.now
