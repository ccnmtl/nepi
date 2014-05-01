from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from pagetree.models import PageBlock
from datetime import datetime
from django import forms


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

    # is submit what happens when the form/section is "submitted"
    def submit(self, user, data):
        '''There are several scenarios which must be accounted for, first we
        have to see if this user has a response for this particular
        conversation scenario - we dont want to create a new one for
        each click, after we know whether to create a new response
        object or to retrieve one we'll decide which of the clicks we
        are are saving

        '''
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
                if rs.first_click == null:
                    # if there is no first click save as first click
                    rs.first_click = conversation
                    rs.save()
                    # is elif sufficient or do I have to explicitly state
                    # if first_click is not null and second_click is null
                elif rs.second_click == null:
                    # if there is a first click but no second click
                    # store as second click if and only if it is not the
                    # same one they clicked on recently
                    # if it is different from the conversation
                    #they previously selected the pageblock is unlocked
                    # otherwise page remains lock and second click is not
                    # recorded
                    if rs.first_click == conversation:
                        break
                    if rs.first_click != conversation:
                        rs.second_click = conversation
                        rs.save()
                        # how do you save something that has been submitted?
                        self.needs_submit() == False
                elif rs.first_click != null and rs.second_click != null:
                    # we want to save the last thing the user clicked on
                    # so when they come back to it the state is preserved
                    rs.third_click = conversation
                    rs.save()

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
        # the user has clicked both conversations
        # it should be safe to use get - there should
        # only be one response per user
        response = ConversationResponse.objects.get(
            conversation=self, user=user)
        if (response.first_click != null and response.second_click != null):
            return True
        else:
            return False


class ConversationScenarioForm(forms.ModelForm):
    class Meta:
        model = ConversationScenario


class Conversation(models.Model):
    scenario = models.ForeignKey(ConversationScenario, null=True,
                                 related_name='conversations')
    text_one = models.CharField(max_length=255, null=True)
    text_two = models.CharField(max_length=255, null=True)
    text_three = models.CharField(max_length=255, null=True)
    complete_dialog = models.CharField(max_length=255, null=True)


class ConvClick(models.Model):
    time = models.DateTimeField(default=datetime.now)
    conversation = models.ForeignKey(Conversation, null=True, blank=True)


class ConversationResponse(models.Model):
    conv_scen = models.ForeignKey(ConversationScenario, null=True, blank=True)
    # Do I need to associate the user with the response here?
    # Its already associated with the section
    user = models.ForeignKey(User, null=True, blank=True)
    first_click = models.ForeignKey(ConvClick, related_name="first_click",
                                    null=True, blank=True)
    second_click = models.ForeignKey(ConvClick, related_name="second_click",
                                     null=True, blank=True)
    last_click = models.ForeignKey(ConvClick, related_name="third_click",
                                   null=True, blank=True)
