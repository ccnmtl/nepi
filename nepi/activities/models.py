from django.db import models
from django import forms
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.utils import simplejson
from pagetree.models import PageBlock
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from datetime import datetime
from django.views.generic.list import ListView
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
        '''There are several scenarios which must be accounted for,
        first we have to see if this user has a response for this particular
        conversation scenario - we dont want to create a new one for each click,
        after we know whether to create a new response object or to retrieve one
        we'll decide which of the clicks we are are saving'''
        rs = ""
        try:
            '''First we need to see if there is a response
            object associated with the scenario already.'''
            rs = ConversationResponse.objects.get(conv_scen=self, user=user)
        except:
            pass
        if rs == "":
            rs = ConversationResponse.objects.create(conv_scen=self, user=user)
        for k in data.keys():
            if k.startswith('conversation-scenario'):
                cid = int(k[len('conversation-scenario-'):])
                conversation = Conversation.objects.get(id=cid)
                if s.first_click == null:
                    pass
                # is elif sufficient or do I have to explicitly state
                # if first_click is not null and second_click is null
                elif s.second_click == null:
                    pass
                elif s.first_click != null and s.second_click != null:
                    pass 

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


class ConversationScenarioListView(ListView):
    template_name = "activities/scenario_list.html"
    model = ConversationScenario
    #context_object_name = "conversation"


    #def get_queryset(self):
    #    self.conversationscenario = get_object_or_404(ConversationScenario, name=self.args[0])
    #    return Conversation.objects.filter(conv_scen=self.conversationscenario)

    #def get_context_data(self, **kwargs):
    #    # Call the base implementation first to get a context
    #    context = super(ConversationScenarioListView, self).get_context_data(**kwargs)
    #    # Add in a QuerySet of all the conversations
    #    context['conversation_list'] = Conversation.objects.all()
    #    return context

    #def get_context_data(self, **kwargs):
    #    context = super(ConversationScenarioListView, self).get_context_data(**kwargs)
    #    context['conversations'] = Conversation.objects.all()


class Conversation(models.Model):
    scenario = models.ForeignKey(ConversationScenario, null=True, related_name='conversations')
    text_one = models.CharField(max_length=255, null=True)
    text_two = models.CharField(max_length=255, null=True)
    text_three = models.CharField(max_length=255, null=True)
    complete_dialog = models.CharField(max_length=255, null=True)


class ConversationForm(forms.ModelForm):
    class Meta:
        model = Conversation
        fields = ['text_one','text_two','text_three','complete_dialog']

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
