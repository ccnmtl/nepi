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
    text_one = models.CharField(max_length=255, null=True, blank=True)
    response_one = models.CharField(max_length=255, null=True, blank=True)
    response_two = models.CharField(max_length=255, null=True, blank=True)
    response_three = models.CharField(max_length=255, null=True, blank=True)
    complete_dialog = models.TextField(max_length=255, null=True, blank=True)


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
        if self.good_conversation is None and self.bad_conversation is None:
           class EditForm(forms.Form):
               alt_text = ("<a href=\"" +
                           reverse("create_conversation", args=[self.id])
                           + "\">add a conversation</a>")
               description = forms.CharField(initial=self.description)
           form = EditForm()
           return form
        elif self.good_conversation is not None and self.bad_conversation is None:
            class EditForm(forms.Form):
                alt_text = ("<a href=\"" +
                            reverse("create_conversation", args=[self.id])
                            + "\">add a bad conversation</a><br><a href=\"" +
                            reverse("update_conversation", args=[self.good_conversation.id])
                            + "\">update good conversation</a>")
                description = forms.CharField(initial=self.description)
            form = EditForm()
            return form
        elif self.good_conversation is None and self.bad_conversation is not None:
            class EditForm(forms.Form):
                alt_text = ("<a href=\"" +
                            reverse("create_conversation", args=[self.id])
                            + "\">add a good conversation</a><br><a href=\"" +
                            reverse("update_conversation", args=[self.bad_conversation.id])
                            + "\">update bad conversation</a>")
                description = forms.CharField(initial=self.description)
            form = EditForm()
            return form
        elif self.good_conversation is not None and self.bad_conversation is not None:
            class EditForm(forms.Form):
                alt_text = ("<a href=\"" +
                            reverse("update_conversation", args=[self.good_conversation.id])
                            + "\">update a good conversation</a><br><a href=\"" +
                            reverse("update_conversation", args=[self.bad_conversation.id])
                            + "\">update bad conversation</a>")
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

    def last_response(self, user):
        try:
            response = ConversationResponse.objects.get(
                conv_scen=self, user=user)
            if (response.first_click is not None
                    and response.second_click is not None):
                return response.third_click.conversation.scenario_type
            elif (response.first_click is not None
                    and response.second_click is None):
                return response.first_click.conversation.scenario_type
        except ConversationResponse.DoesNotExist:
            return 0


# dont think I need this
class ConversationForm(forms.ModelForm):
    class Meta:
        model = Conversation


class ConversationScenarioForm(forms.ModelForm):
    class Meta:
        model = ConversationScenario
        exclude = ('good_conversation', 'bad_conversation',)


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
    
#     def save_click(self, new_click):
#         if self.first_click is None:
#             print "inside first is none..."
#             self.first_click = new_click
#             self.save()
#             return True
#         if self.first_click is not None and self.second_click is None:
#             print "inside second is none..."
#             self.second_click = new_click
#             self.third_click = new_click
#             self.save()
#             return True
#         if rs.second_click is not None:
#             print "inside third is not none..."
#             self.third_click = new_click
#             print "inside third is not none..."
#             self.save()
#             return True
    

class ImageMapItem(models.Model):
    label_name = models.CharField(max_length=64, default='')
    label = models.CharField(max_length=64)
    content = models.TextField()
    map_area_shape = models.CharField(max_length=64, default='')
    coordinates = models.TextField()

    def __unicode__(self):
        return self.label_name


class ImageMapChart(models.Model):
    pageblocks = generic.GenericRelation(PageBlock)
    template_file = "activities/imagemapchart.html"
    js_template_file = "activities/imagemapchart_js.html"
    css_template_file = "activities/imagemapchart_css.html"
    display_name = "Interactive Image Map Chart"
    intro_text = models.TextField(default='')

    items = models.ManyToManyField(ImageMapItem)

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __unicode__(self):
        return unicode(self.pageblock())

    def needs_submit(self):
        return False

    @classmethod
    def add_form(self):
        return ImageMapChartForm()

    def edit_form(self):
        return ImageMapChartForm(instance=self)

    @classmethod
    def create(self, request):
        form = ImageMapChartForm(request.POST)
        return form.save()

    def edit(self, vals, files):
        form = ImageMapChartForm(data=vals, files=files, instance=self)
        if form.is_valid():
            form.save()

    def unlocked(self, user):
        return True


class ImageMapChartForm(forms.ModelForm):
    class Meta:
        model = ImageMapChart
