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

    def submit(self, user, data):
        s = ConversationResponse.objects.create(conversation=self, user=user)
        for k in data.keys():
            if k.startswith('conversation-scenario'):
                cid = int(k[len('conversation-scenario-'):])
                conversation = ConversationScenario.objects.get(id=cid)

    @classmethod
    def add_form(self):
        class AddForm(forms.Form):
            description = forms.CharField(widget=forms.widgets.Textarea())
        return AddForm()

# is this what its supposed to look like
#    @classmethod
#    def create(self, request):
#        form = CounselingSessionForm(request.POST)
#        return form.save()

    @classmethod
    def create(self, request):
        return ConversationScenario.objects.create(
            description=request.POST.get('description', ''))

    def edit_form(self):
        class ConversationScenarioForm(forms.ModelForm):
            class Meta:
                model = ConversationScenario
                fields = ('description')
        return ConversationScenarioForm()

    def edit(self, vals):
        self.description = vals.get('description', '')
        self.save()

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
        # next activity becomes unlocked when
        # the user has seen both good and bad dialog
        return ConversationResponse.objects.filter(
            conversation=self, user=user)

    def add_conversationo(self, request=None):
        return ConversationScenarioForm(request)


class CreateConversationScenarioView(CreateView): 
    model = ConversationScenario 
    template_name = 'main/add_conversation.html' 
    success_url = '/thank_you/' 


class UpdateConversationScenarioView(UpdateView): 
    model = ConversationScenario 
    template_name = 'main/add_conversation.html' 
    success_url = '/thank_you/' 


class Conversation(models.Model):
    scenario = models.ForeignKey(ConversationScenario, null=True)
    text_one = models.CharField(max_length=255, null=True)
    text_two = models.CharField(max_length=255, null=True)
    text_three = models.CharField(max_length=255, null=True)
    complete_dialog = models.CharField(max_length=255, null=True)


#class Conversation(forms.ModelForm):
#    class Meta:
#        model = Conversation
#        fields = ('text_one', 'text_two', 'text_three', 'complete_dialog')


class CreateConversationView(CreateView): 
    model = Conversation 
    template_name = 'main/add_conversation.html' 
    success_url = '/thank_you/' 


class UpdateConversationView(UpdateView): 
    model = Conversation 
    template_name = 'main/add_conversation.html' 
    success_url = '/thank_you/' 


class ConversationResponse(models.Model):
    conversation = models.ForeignKey(ConversationScenario)
    user = models.ForeignKey(User)
    submitted = models.DateTimeField(default=datetime.now)


