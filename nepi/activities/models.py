from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from pagetree.models import PageBlock
from datetime import datetime
from django import forms


CONV_CHOICES = (
        ('G', 'Good'),
        ('B', 'Bad'),
    )


class Conversation(models.Model):
    starting = models.BooleanField(default=True)
    scenario_type = models.CharField(max_length=1, choices=CONV_CHOICES, default='G')
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
    
    good_conversation = models.ForeignKey(Conversation, null=True, related_name='good_conversation')
    bad_conversation = models.ForeignKey(Conversation, null=True, related_name='bad_conversation')

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
                conversation = Conversation.objects.get(id=cid)
                if rs.first_click == null:
                    rs.first_click = conversation
                    rs.save()
                    self.needs_submit() == True
                elif rs.second_click == null:
                    if rs.first_click == conversation:
                        self.needs_submit() == True
                    if rs.first_click != conversation:
                        rs.second_click = conversation
                        rs.third_click = conversation
                        rs.save()
                        self.needs_submit() == False
                elif rs.first_click != null and rs.second_click != null:
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
        response = ConversationResponse.objects.get(
            conversation=self, user=user)
        if (response.first_click != null and response.second_click != null):
            return True
        else:
            return False


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
    last_click = models.ForeignKey(ConvClick, related_name="third_click",
                                   null=True, blank=True)
