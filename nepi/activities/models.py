from django.db import models
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.utils import simplejson
from pagetree.models import PageBlock
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from datetime import datetime
from django import forms

class ConversationScenario(models.Model):
    pageblocks = generic.GenericRelation(PageBlock)
    description = models.TextField(blank=True)
    display_name = "Conversation Scenario"
    template_name = "activities/conversation.html"
    exportable = False
    importable = False

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __unicode__(self):
        return unicode(self.pageblock())

    def needs_submit(self):
        return True

    def submit(self, user, data):
        rs, created = ConversationResponse.objects.get_or_create(conv_scen=self, user=user)
        for k in data.keys():
            if k.startswith('conversation-scenario'):
                cid = int(k[len('conversation-scenario-'):])
                # for some reason had trouble getting this in view may need to query for object inside if statement
                conversation = Conversation.objects.get(id=cid)
                if rs.first_click == null:
                    rs.first_click = conversation
                    rs.save()
                    # Should I be returning True or False?
                    # return True # assuming True = still needs_submit
                    self.needs_submit() == True
                elif rs.second_click == null:
                    if rs.first_click == conversation:
                        # what to do if user clicks same conversation twice?
                        # assume just return needs to be submitted without saving anything
                        # return True # assuming True = still needs_submit
                        self.needs_submit() == True
                    if rs.first_click != conversation:
                        rs.second_click = conversation
                        rs.third_click = conversation
                        # we should set third click - as of now block is "submitted and last click is second click"
                        rs.save()
                        # how do you save something that has been submitted?
                        self.needs_submit() == False
                elif rs.first_click != null and rs.second_click != null:
                    # we want to save the last thing the user clicked on
                    # so when they come back to it the state is preserved
                    rs.third_click = conversation
                    rs.save()
                    self.needs_submit() == False
    
    @classmethod
    def add_form(self):
        return ConversationScenarioForm()

    def edit_form(self):
         return ConversationScenarioForm()#instance=self)

    @classmethod
    def create(self, request):
        form = ConversationScenarioForm(request.POST)
        return form.save()

    def edit(self, vals, files):
        form = ConversationScenarioForm(data=vals, files=files, instance=self)
        if form.is_valid():
            form.save()

    def redirect_to_self_on_submit(self):
        # show the student feedback before proceeding
        return True

    def unlocked(self, user):
        # next activity becomes unlocked when
        # the user has clicked both conversations
        # it should be safe to use get - there should
        # only be one response per user
        response = ConversationResponse.objects.get(
            conversation=self, user=user)
        if response.first_click != null \
            and response.second_click != null :
            return True
        else:
            return False


class ConversationScenarioForm(forms.ModelForm):
    class Meta:
        model = ConversationScenario



class Conversation(models.Model):
    CONV_CHOICES = (
        ('G', 'Good'),
        ('B', 'Bad'),
    )
    starting_conv = models.BooleanField(default=True)
    conversation_type = models.CharField(max_length=1, choices=CONV_CHOICES, default='G')
    scenario = models.ForeignKey(ConversationScenario, null=True, related_name='conversations')
    text_one = models.CharField(max_length=255, null=True)
    text_two = models.CharField(max_length=255, null=True)
    text_three = models.CharField(max_length=255, null=True)
    complete_dialog = models.CharField(max_length=255, null=True)

    
class ConvClick(models.Model):
    created = models.DateTimeField(default=datetime.now)
    conversation = models.ForeignKey(Conversation, null=True, blank=True)


class ConversationResponse(models.Model):
    conv_scen = models.ForeignKey(ConversationScenario, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)
    first_click = models.ForeignKey(ConvClick, related_name="first_click", null=True, blank=True)
    second_click = models.ForeignKey(ConvClick, related_name="second_click", null=True, blank=True)
    last_click = models.ForeignKey(ConvClick, related_name="third_click", null=True, blank=True)
    
#    def record_get_click(self, conversation_info):
#        for k in data.keys():
#            if k.startswith('conversation-id'):
#                cid = int(k[len('conversation-id-'):])
#                conversation = Conversation.objects.get(id=cid)
#            if k.startswith('conversation-scenario'):
#                sid = int(k[len('conversation-id-'):])
#                conv_scenario = ConversationScenario.objects.get(id=sid)
            