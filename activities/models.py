from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.db.models.query_utils import Q
from django.db.models.signals import pre_save, post_init
from django.dispatch.dispatcher import receiver
from django.utils import simplejson
from operator import itemgetter
from pagetree.models import PageBlock
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from datetime import datetime


START_CONV = (
    ('P', 'Patient'),
    ('N', 'Nurse'),
)

CONV_STATUS = (
    ('R', 'Right'),
    ('W', 'Wrong'),
)

class NurseConversation(models.Model):
    starting = models.CharField(max_length=255)
    response_one = models.CharField(max_length=255)
    response_two = models.CharField(max_length=255)


class PatientConversation(models.Model):
    starting = models.CharField(max_length=255)
    response_one = models.CharField(max_length=255)
    response_two = models.CharField(max_length=255)


class ConversationDialog(models.Model):
    order = models.PositiveIntegerField()
    content = models.CharField(max_length=255)


class ConversationScenario(models.Model):
    starting_party = models.CharField(max_length=1, choices=START_CONV, blank=True)
    nurse_bubbles = models.ForeignKey(NurseConversation)
    patient_bubbles = models.ForeignKey(PatientConversation)
    dialog = models.ForeignKey(ConversationDialog)


class Conversation(models.Model):
    good_conversation = models.ForeignKey(ConversationScenario, related_name="good_conversation")
    bad_conversation = models.ForeignKey(ConversationScenario, related_name="bad_conversation")
    directions = models.TextField(blank=True)
    pageblocks = generic.GenericRelation(PageBlock)
    # how to deal with templates?
    exportable = False
    importable = False

    def needs_submit(self):
        return True

    def redirect_to_self_on_submit(self):
        # show the student feedback before proceeding
        return True

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __unicode__(self):
        return unicode(self.pageblock())

    def unlocked(self, user):
        # next activity becomes unlocked when the user has seen both good and bad dialog
        return ConversationSubmission.objects.filter(conversation=self, user=user).second_selection


class ConversationSubmission(models.Model):
    conversation = models.ForeignKey(Conversation)
    user = models.ForeignKey(User)
    submitted = models.DateTimeField(default=datetime.now)
    first_click = models.CharField(max_length=1, choices=CONV_STATUS, blank=True)
    second_selection = models.BooleanField(default=False)

    def __unicode__(self):
        return "activity %d submission by %s at %s" % (self.conversation.id,
                                                   unicode(self.user),
                                                   self.submitted)

    def is_correct(self):
        if self.first_click == R:
            return True
        if self.first_click == W:
            return False


