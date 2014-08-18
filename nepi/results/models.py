# from django.db import models
from django.contrib.auth.models import User
# from django.contrib.contenttypes import generic
# from pagetree.models import PageBlock, Quiz, Submission
# from datetime import datetime
# from django import forms
# from django.core.urlresolvers import reverse
# from nepi.main.models import UserProfile
from nepi.activities.models import ConversationResponse, \
    ConversationScenario


# for a user grab their three conversation responses

# we don't need to filter by hierarchy yet
conversation_scenarios = ConversationScenario.objects.all()


def get_conversation_responses(user, conv_scen):
    user = User.objects.get(user=user)
    user_responses = ConversationResponse.objects.filter(user=user,
                                                         conv_scen=conv_scen)
    return user_responses
