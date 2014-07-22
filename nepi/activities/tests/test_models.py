from factories import ConversationScenarioFactory, \
    ConvClickFactory, GoodConversationFactory, \
    ConversationPageblockHierarchyFactory
from nepi.main.tests.factories import UserFactory
from django.test import TestCase
from nepi.activities.models import ConversationResponse


class TestConvClick(TestCase):
    def test_unicode(self):
        c = ConvClickFactory()
        self.assertEqual(str(c), "G Click")


class TestConversation(TestCase):
    def test_unicode(self):
        g = GoodConversationFactory()
        self.assertEqual(str(g), "G")


class TestConversationScenario(TestCase):
    def test_unicode(self):
        c = ConversationPageblockHierarchyFactory()
        self.assertEqual(str(c), "conv_hierarchy")


class TestConversationResponse(TestCase):
    def test_unicode(self):
        pass
        # c = ConversationResponse()
        # self.assertEqual(str(c), "Testing ConversationScenario")


class TestUserConversationScenario(TestCase):
    '''We want to make sure we can create a conversation
     response associated with the user upon submission.'''

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
        # self.assertTrue(scenario.needs_submit())
        '''Test second click'''
        cr.second_click = click_two
        cr.save()
        self.assertEquals(click_two.conversation.scenario_type,
                          cr.second_click.conversation.scenario_type)
        self.assertIsNone(cr.third_click)
        self.assertTrue(scenario.unlocked(user))
        '''Test third click'''
        cr.third_click = click_three
        cr.save()
        self.assertEquals(click_three.conversation.scenario_type,
                          cr.third_click.conversation.scenario_type)
        self.assertIsNotNone(cr.third_click)
        self.assertTrue(scenario.unlocked(user))


# class TestCalendarActivity(TestCase):
#     pass

class TestDosageActivity(TestCase):
    pass
