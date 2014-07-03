from django.contrib.auth.models import User
import factory
from nepi.activities.models import ConversationScenario, \
    Conversation, ConversationResponse, ConvClick


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: "user%d" % n)


class GoodConversationFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Conversation
    text_one = "We assume text one is the starting text"
    response_one = "Text 1 is the response to whatever the other party says"
    response_two = "Text 2 is the response to whatever the other party says"
    response_three = "Text 3 is an optional response/thought to " + \
        "whatever the other party says"
    complete_dialog = "This is the entire Nurse/Patient exchange" + \
        " that is displayed when the user selects the starting text"


class BadConversationFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Conversation
    text_one = "We assume text one is the starting text"
    response_one = "Text 1 is the response to whatever the other party says"
    response_two = "Text 2 is the response to whatever the other party says"
    response_three = "Text 3 is an optional response/thought to " + \
        "whatever the other party says"
    complete_dialog = "This is the entire Nurse/Patient exchange" + \
        " that is displayed when the user selects the starting text"


class ConversationScenarioFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ConversationScenario
    description = "Description for the Conversation Scenario"
    '''do I even need a good and bad factory? doesn't really matter
    except for how it is save here in the scenario.'''
    good_conversation = factory.SubFactory(GoodConversationFactory)
    bad_conversation = factory.SubFactory(BadConversationFactory)


class ConvClickFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ConvClick
    conversation = factory.SubFactory(GoodConversationFactory)


class ConversationResponseFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ConversationResponse
    user = factory.SubFactory(UserFactory)
    conv_scen = factory.SubFactory(ConversationScenarioFactory)
