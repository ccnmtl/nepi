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
from quizblock.models import Quiz, Answer, Question, Submission
from pagetree.models import PageBlock
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse


START_CONV = (
    ('P', 'Patient'),
    ('N', 'Nurse'),
)

# current plan: starting party may have one or two
# speech elements to start with, there may be one
# or more responses, 

class NurseConversation(models.Model):
    starting_one = models.CharField(max_length=255)
    starting_two = models.CharField(max_length=255)
    response_one = models.CharField(max_length=255)
    response_two = models.CharField(max_length=255)


class PatientConversation(models.Model):    
    starting_one = models.CharField(max_length=255)
    starting_two = models.CharField(max_length=255)
    responseg_one = models.CharField(max_length=255)
    response_two = models.CharField(max_length=255)

class ConversationDialog(models.Model):
    pass
#need to make a back and forth ordered dialog


class Conversation(models.Model):
    # should blank be True?
    starting_party = models.CharField(max_length=2, choices=START_CONV, blank=True)
    directions = models.TextField(blank=True)
    explanation = models.TextField(blank=True)
    first_click = models.BooleanField(default=False)
    pageblocks = generic.GenericRelation(PageBlock)
    # how to deal with templates?
    exportable = False
    importable = False




