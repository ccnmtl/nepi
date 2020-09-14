from decimal import Decimal
import factory
from nepi.activities.models import ConversationScenario, \
    Conversation, ConvClick, RetentionRateCard, RetentionClick, \
    CalendarChart, Month, Day, DosageActivity, \
    ImageInteractive, ARTCard, AdherenceCard


class GoodConversationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Conversation
    text_one = "We assume text one is the starting text"
    response_one = "Text 1 is the response to whatever the other party says"
    response_two = "Text 2 is the response to whatever the other party says"
    response_three = "Text 3 is an optional response/thought to " + \
        "whatever the other party says"
    complete_dialog = "This is the entire Nurse/Patient exchange" + \
        " that is displayed when the user selects the starting text"


class BadConversationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Conversation
    text_one = "We assume text one is the starting text"
    response_one = "Text 1 is the response to whatever the other party says"
    response_two = "Text 2 is the response to whatever the other party says"
    response_three = "Text 3 is an optional response/thought to " + \
        "whatever the other party says"
    complete_dialog = "This is the entire Nurse/Patient exchange" + \
        " that is displayed when the user selects the starting text"


class ConversationScenarioFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ConversationScenario
    description = "Description for the Conversation Scenario"
    '''do I even need a good and bad factory? doesn't really matter
    except for how it is save here in the scenario.'''
    good_conversation = factory.SubFactory(GoodConversationFactory)
    bad_conversation = factory.SubFactory(BadConversationFactory)


class ConvClickFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ConvClick
    conversation = factory.SubFactory(GoodConversationFactory)


class RetentionRateCardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RetentionRateCard
    intro_text = "intro text"


class RetentionClickFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RetentionClick
    click_string = "cohort_click"


class MonthFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Month
    display_name = "January 2015"


class CalendarChartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CalendarChart
    month = factory.SubFactory(MonthFactory)
    correct_date = 4
    description = 'description'


class IncorrectDayOneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Day
    calendar = factory.SubFactory(MonthFactory)
    number = 1
    explanation = "This is the wrong day"


class IncorrectDayTwoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Day
    calendar = factory.SubFactory(MonthFactory)
    number = 2
    explanation = "This is the wrong day"


class CorrectDayFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Day
    calendar = factory.SubFactory(MonthFactory)
    number = 4
    explanation = "This is the correct day"


class ImageInteractiveFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ImageInteractive
    intro_text = "intro text"


class ARTCardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ARTCard
    intro_text = "intro text"


class AdherenceCardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AdherenceCard
    quiz_class = "quiz class"


class DosageActivityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DosageActivity
    explanation = 'the explanation'
    question = 'the question'
    ml_nvp = Decimal(1.5)
    times_day = 3
    weeks = 5
