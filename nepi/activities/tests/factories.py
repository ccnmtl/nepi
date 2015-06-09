import factory
from nepi.activities.models import ConversationScenario, \
    Conversation, ConvClick, RetentionRateCard, RetentionClick, \
    CalendarChart, Month, Day, DosageActivity, \
    ImageInteractive, ARTCard, AdherenceCard


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


class RetentionRateCardFactory(factory.DjangoModelFactory):
    FACTORY_FOR = RetentionRateCard
    intro_text = "intro text"


class RetentionClickFactory(factory.DjangoModelFactory):
    FACTORY_FOR = RetentionClick
    click_string = "cohort_click"


class MonthFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Month
    display_name = "January 2015"


class CalendarChartFactory(factory.DjangoModelFactory):
    FACTORY_FOR = CalendarChart
    month = factory.SubFactory(MonthFactory)
    correct_date = 4
    description = 'description'


class IncorrectDayOneFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Day
    calendar = factory.SubFactory(MonthFactory)
    number = 1
    explanation = "This is the wrong day"


class IncorrectDayTwoFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Day
    calendar = factory.SubFactory(MonthFactory)
    number = 2
    explanation = "This is the wrong day"


class CorrectDayFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Day
    calendar = factory.SubFactory(MonthFactory)
    number = 4
    explanation = "This is the correct day"


class ImageInteractiveFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ImageInteractive


class ARTCardFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ARTCard


class AdherenceCardFactory(factory.DjangoModelFactory):
    FACTORY_FOR = AdherenceCard


class DosageActivityFactory(factory.DjangoModelFactory):
    FACTORY_FOR = DosageActivity
    explanation = "the explanation"
    question = "the question"
    ml_nvp = 1.5
    times_day = 2
    weeks = 6
