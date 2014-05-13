from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from pagetree.models import PageBlock
from datetime import datetime
from django import forms
from django.core.urlresolvers import reverse


CONV_CHOICES = (
    ('G', 'Good'),
    ('B', 'Bad'),
)


class Conversation(models.Model):
    scenario_type = models.CharField(max_length=1, choices=CONV_CHOICES,
                                     default='G')
    text_one = models.CharField(max_length=255, null=True)
    response_one = models.CharField(max_length=255, null=True)
    response_two = models.CharField(max_length=255, null=True)
    response_three = models.CharField(max_length=255, null=True)
    complete_dialog = models.CharField(max_length=255, null=True)


class ConversationScenario(models.Model):
    pageblocks = generic.GenericRelation(PageBlock)
    description = models.TextField(blank=True)
    display_name = "Conversation Scenario"
    template_file = "activities/conversation.html"
    js_template_file = "activities/conversation_js.html"
    css_template_file = "activities/conversation_css.html"
    exportable = False
    importable = False
    good_conversation = models.ForeignKey(Conversation, null=True, blank=True,
                                          related_name='good_conversation')
    bad_conversation = models.ForeignKey(Conversation, null=True, blank=True,
                                         related_name='bad_conversation')

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __unicode__(self):
        return unicode(self.pageblock())

    def needs_submit(self):
        '''Pageblock will see that block has needs
        submit and then check the conditions defined
        in "unlocked to determine if it is unlocked or not."'''
        return True

    @classmethod
    def add_form(self):
        return ConversationScenarioForm()

    def edit_form(self):
        class EditForm(forms.Form):
            alt_text = ("<a href=\"" +
                        reverse("create_conversation", args=[self.id])
                        + "\">add a conversation</a>")
            description = forms.CharField(initial=self.description)
        form = EditForm()
        return form

    @classmethod
    def create(self, request):
        form = ConversationScenarioForm(request.POST)
        return form.save()

    def edit(self, vals, files):
        form = ConversationScenarioForm(data=vals, files=files, instance=self)
        if form.is_valid():
            form.save()

    def redirect_to_self_on_submit(self):
        '''Show student feedback before proceeding,
        not sure if this is ever called since there is no "submit"'''
        return True

    def unlocked(self, user):
        '''We want to make sure the user has selected both dialogs
           from the conversation before they can proceed.'''
        response = ConversationResponse.objects.filter(
            conv_scen=self, user=user)
        if (len(response) == 1
                and response[0].first_click is not None
                and response[0].second_click is not None):
            return True
        else:
            return False


class ConversationForm(forms.ModelForm):
    class Meta:
        model = Conversation


class ConversationScenarioForm(forms.ModelForm):
    class Meta:
        model = ConversationScenario


class ConvClick(models.Model):
    created = models.DateTimeField(default=datetime.now)
    conversation = models.ForeignKey(Conversation, null=True, blank=True)


class ConversationResponse(models.Model):
    conv_scen = models.ForeignKey(ConversationScenario, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)
    first_click = models.ForeignKey(ConvClick, related_name="first_click",
                                    null=True, blank=True)
    second_click = models.ForeignKey(ConvClick, related_name="second_click",
                                     null=True, blank=True)
    third_click = models.ForeignKey(ConvClick, related_name="third_click",
                                    null=True, blank=True)
