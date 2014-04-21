from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.utils import simplejson
from pagetree.models import PageBlock
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from datetime import datetime


START_CONV = (
    ('P', 'Patient'),
    ('N', 'Nurse'),
)


class NurseConversation(models.Model):
    dialog_one = models.CharField(max_length=255, null=True)
    dialog_two = models.CharField(max_length=255, null=True)


class NurseConversationForm(forms.ModelForm):
    class Meta:
        model = NurseConversation
        fields = ('dialog_one', 'dialog_two')


class PatientConversation(models.Model):
    dialog_one = models.CharField(max_length=255, null=True)
    dialog_two = models.CharField(max_length=255, null=True)


class PatientConversationForm(forms.ModelForm):
    class Meta:
        model = PatientConversation
        fields = ('dialog_one', 'dialog_two')


class ConversationDialog(models.Model):
    order = models.PositiveIntegerField()
    content = models.CharField(max_length=255)


class ConversationDialogForm(forms.ModelForm):
    class Meta:
        model = ConversationDialog
        fields = ('order', 'content')


class ConversationScenario(models.Model):
    starting_party = models.CharField(
        max_length=1, choices=START_CONV, null=True, blank=True)
    nurse_bubbles = models.ForeignKey(NurseConversation)
    patient_bubbles = models.ForeignKey(PatientConversation)
    # I think the foriegn keys probably belong in the sub models...
    dialog = models.ForeignKey(ConversationDialog)


class ConversationScenarioForm(forms.ModelForm):
    # is it smart enough to create the sub fields as forms?
    class Meta:
        model = ConversationScenario
        fields = ('starting_party',
                  'nurse_bubbles',
                  'patient_bubbles',
                  'dialog')


class Conversation(models.Model):
    good_conversation = models.ForeignKey(
        ConversationScenario, related_name="good_conversation", null=True)
    bad_conversation = models.ForeignKey(
        ConversationScenario, related_name="bad_conversation", null=True)
    description = models.TextField(blank=True)
    pageblocks = generic.GenericRelation(PageBlock)
    display_name = "Conversation"
    template_name = "activities/conversation.html"
    exportable = False
    importable = False

    def submit(self, user, data):
        s = ConversationResponse.objects.create(conversation=self, user=user)
        for k in data.keys():
            if k.startswith('conversation-scenario'):
                cid = int(k[len('conversation-scenario-'):])
                conversation = ConversationScenario.objects.get(id=cid)
                if s.first_click == "":
                    s.first_click = conversation.related_name
                    s.save()
                elif s.first_click != "":
                    if s.first_click == conversation.related_name:
                        pass
                    elif s.first_click != conversation.related_name:
                        second_click = True

    @classmethod
    def add_form(self):
        class AddForm(forms.Form):
            description = forms.CharField(widget=forms.widgets.Textarea())
        return AddForm()

    @classmethod
    def create(self, request):
        return Conversation.objects.create(
            description=request.POST.get('description', ''))

    def edit_form(self):
        class EditForm(forms.Form):
            description = forms.CharField(
                widget=forms.widgets.Textarea(),
                initial=self.description)
            good_conversation = ConversationScenarioForm()
        return EditForm()

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
            conversation=self, user=user).second_selection

    def add_nurse_conversation(self, request=None):
        return NurseConversationForm(request)

    def add_patient_conversation(self, request=None):
        return PatientConversationForm(request)

    def add_conversation_dialog(self, request=None):
        return ConversationDialogForm(request)

    def add_conversation_scenario(self, request=None):
        return ConversationScenarioForm(request)


class ConversationResponse(models.Model):
    conversation = models.ForeignKey(Conversation)
    user = models.ForeignKey(User)
    submitted = models.DateTimeField(default=datetime.now)
    first_click = models.CharField(max_length=255, blank=True)
    second_selection = models.BooleanField(default=False)

    def get_second_click(self, request):
        '''User should only be able to continue after
        having clicked on both conversations'''
        if request.POST.get('click') == self.first_click:
            self.second_selection = False
        if request.POST.get('click') != self.first_click:
            self.second_selection = True
