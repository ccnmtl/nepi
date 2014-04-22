from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.utils import simplejson
from pagetree.models import PageBlock
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from datetime import datetime
from django.views.generic.edit import CreateView, UpdateView


class ConversationScenario(models.Model):
    description = models.TextField(blank=True)
    pageblocks = generic.GenericRelation(PageBlock)
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
        s = ConversationResponse.objects.create(conversation=self, user=user)
        for k in data.keys():
            if k.startswith('conversation-scenario'):
                cid = int(k[len('conversation-scenario-'):])
                conversation = ConversationScenario.objects.get(id=cid)

    @classmethod
    def add_form(self):
        return ConversationScenarioForm()

    def edit_form(self):
        return ConversationScenarioForm(instance=self)

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
        # the user has seen both good and bad dialog
        return ConversationResponse.objects.filter(
            conversation=self, user=user)


class ConversationScenarioForm(forms.ModelForm):
    class Meta:
        model = ConversationScenario


class Conversation(models.Model):
    scenario = models.ForeignKey(ConversationScenario, null=True)
    text_one = models.CharField(max_length=255, null=True)
    text_two = models.CharField(max_length=255, null=True)
    text_three = models.CharField(max_length=255, null=True)
    complete_dialog = models.CharField(max_length=255, null=True)


class CreateConversationView(CreateView):
    model = Conversation
    template_name = 'main/add_conversation.html'
    success_url = '/thank_you/'


class UpdateConversationView(UpdateView):
    model = Conversation
    template_name = 'main/add_conversation.html'
    success_url = '/thank_you/'


class ConvClick(models.Model):
    time = models.DateTimeField(default=datetime.now)
    conversation = models.ForeignKey(Conversation, null=True, blank=True)
    
    def get_click(self, request):
        pass


class ConversationResponse(models.Model):
    conv_scen = models.ForeignKey(ConversationScenario, null=True, blank=True)
    user = models.ForeignKey(User)
    first_click = models.ForeignKey(ConvClick, related_name="first_click", null=True, blank=True)
    second_click = models.ForeignKey(ConvClick, related_name="second_click", null=True, blank=True)
    last_click = models.ForeignKey(ConvClick, related_name="third_click", null=True, blank=True)
