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

    def __unicode__(self):
#        scenario = ConversationScenario.objects.get(Q(good_conversation==self)
#  | Q(bad_conversation==self))
        return unicode(self.scenario_type)


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
        in "unlocked" to determine if it is unlocked or not.'''
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
        elif (self.good_conversation is not None
              and self.bad_conversation is None):
                class EditForm(forms.Form):
                    alt_text = ("<a href=\"" +
                                reverse("create_conversation", args=[self.id])
                                + "\">add a bad conversation</a><br>" +
                                "<a href=\"" +
                                reverse("update_conversation",
                                        args=[self.good_conversation.id])
                                + "\">update good conversation</a>")
                    description = forms.CharField(initial=self.description)
                form = EditForm()
                return form
        elif (self.good_conversation is None
              and self.bad_conversation is not None):
                class EditForm(forms.Form):
                    alt_text = ("<a href=\"" +
                                reverse("create_conversation", args=[self.id])
                                + "\">add a good conversation</a><br>" +
                                "<a href=\"" +
                                reverse("update_conversation",
                                        args=[self.bad_conversation.id])
                                + "\">update bad conversation</a>")
                    description = forms.CharField(initial=self.description)
                form = EditForm()
                return form
        elif (self.good_conversation is not None
              and self.bad_conversation is not None):
                class EditForm(forms.Form):
                    alt_text = ("<a href=\"" +
                                reverse("update_conversation",
                                        args=[self.good_conversation.id])
                                + "\">update a good conversation</a><br>" +
                                "<a href=\"" +
                                reverse("update_conversation",
                                        args=[self.bad_conversation.id])
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

    def __unicode__(self):
        return("Response to " + (self.conv_scen))


class ImageInteractive(models.Model):
    pageblocks = generic.GenericRelation(PageBlock)
    template_file = "activities/imagemapchart.html"
    js_template_file = "activities/imagemapchart_js.html"
    css_template_file = "activities/imagemapchart_css.html"
    display_name = "Image Interactive"
    intro_text = models.TextField(default='')

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __unicode__(self):
        return unicode(self.pageblock())

    def needs_submit(self):
        return False

    @classmethod
    def add_form(self):
        return ImageInteractiveForm()

    def edit_form(self):
        return ImageInteractiveForm(instance=self)

    @classmethod
    def create(self, request):
        form = ImageInteractiveForm(request.POST)
        return form.save()

    def edit(self, vals, files):
        form = ImageInteractiveForm(data=vals, files=files, instance=self)
        if form.is_valid():
            form.save()

    def unlocked(self, user):
        return True


class ImageInteractiveForm(forms.ModelForm):
    class Meta:
        model = ImageInteractive


class ARTCard(models.Model):
    pageblocks = generic.GenericRelation(PageBlock)
    template_file = "activities/artcard.html"
    js_template_file = "activities/artcard_js.html"
    css_template_file = "activities/artcard_css.html"
    display_name = "ART Card"
    intro_text = models.TextField(default='')

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __unicode__(self):
        return unicode(self.pageblock())

    def needs_submit(self):
        return False

    @classmethod
    def add_form(self):
        return ARTCardForm()

    def edit_form(self):
        return ARTCardForm(instance=self)

    @classmethod
    def create(self, request):
        form = ARTCardForm(request.POST)
        return form.save()

    def edit(self, vals, files):
        form = ARTCardForm(data=vals, files=files, instance=self)
        if form.is_valid():
            form.save()

    def unlocked(self, user):
        return True


class ARTCardForm(forms.ModelForm):
    class Meta:
        model = ARTCard


class RetentionRateCard(models.Model):
    pageblocks = generic.GenericRelation(PageBlock)
    template_file = "activities/retentionrate.html"
    js_template_file = "activities/retentionrate_js.html"
    css_template_file = "activities/retentionrate_css.html"
    display_name = "Retention Rate Card"
    intro_text = models.TextField(default='')

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __unicode__(self):
        return unicode(self.pageblock())

    def needs_submit(self):
        return True

    @classmethod
    def add_form(self):
        return RetentionRateCardForm()

    def edit_form(self):
        return RetentionRateCardForm(instance=self)

    @classmethod
    def create(self, request):
        form = RetentionRateCardForm(request.POST)
        return form.save()

    def edit(self, vals, files):
        form = RetentionRateCardForm(data=vals, files=files, instance=self)
        if form.is_valid():
            form.save()

    def redirect_to_self_on_submit(self):
        '''Show student feedback before proceeding,
        not sure if this is ever called since there is no "submit"'''
        return True

    def unlocked(self, user):
        '''We want to make sure the user has selected all clickable
           parts of the table before they are allowed to proceed.'''
        response = RetentionResponse.objects.filter(
            conv_scen=self, user=user)
        if (len(response) == 1
                and response[0].cohort_click is not None
                and response[0].start_date_click is not None
                and response[0].eligible_click is not None
                and response[0].delivery_date_click is not None
                and response[0].dec_click is not None
                and response[0].jan_click is not None
                and response[0].feb_click is not None
                and response[0].mar_click is not None
                and response[0].apr_click is not None
                and response[0].may_click is not None
                and response[0].jun_click is not None):
            return True
        else:
            return False


class RetentionRateCardForm(forms.ModelForm):
    class Meta:
        model = RetentionRateCard


class RetentionClick(models.Model):
    created = models.DateTimeField(default=datetime.now)
    click_string = models.CharField(max_length=50)


class RetentionResponse(models.Model):
    retentionrate = models.ForeignKey(RetentionRateCard, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)
    cohort_click = models.ForeignKey(RetentionClick,
                                     related_name="retention_cohort_click",
                                     null=True, blank=True)
    start_date_click = models.ForeignKey(
        RetentionClick,
        related_name="retention_start_date_click",
        null=True, blank=True)
    eligible_click = models.ForeignKey(RetentionClick,
                                       related_name="retention_eligible_click",
                                       null=True, blank=True)
    delivery_date_click = models.ForeignKey(
        RetentionClick,
        related_name="retention_delivery_date_click",
        null=True, blank=True)
    dec_click = models.ForeignKey(RetentionClick,
                                  related_name="retention_dec_click",
                                  null=True, blank=True)
    jan_click = models.ForeignKey(RetentionClick,
                                  related_name="retention_jan_click",
                                  null=True, blank=True)
    feb_click = models.ForeignKey(RetentionClick,
                                  related_name="retention_feb_click",
                                  null=True, blank=True)
    mar_click = models.ForeignKey(RetentionClick,
                                  related_name="retention_mar_click",
                                  null=True, blank=True)
    apr_click = models.ForeignKey(RetentionClick,
                                  related_name="retention_apr_click",
                                  null=True, blank=True)
    may_click = models.ForeignKey(RetentionClick,
                                  related_name="retention_may_click",
                                  null=True, blank=True)
    jun_click = models.ForeignKey(RetentionClick,
                                  related_name="retention_jun_click",
                                  null=True, blank=True)

    def __unicode__(self):
        return("Response to " + str(self.retentionrate))


class CalendarChart(models.Model):
    pageblocks = generic.GenericRelation(PageBlock)
    template_file = "activities/calendarchart.html"
    js_template_file = "activities/calendarchart_js.html"
    css_template_file = "activities/calendarchart_css.html"
    display_name = "Calendar Chart"
    description = models.TextField(default='')
    birth_date = models.IntegerField(default=0)
    appointment = models.IntegerField(default=0)

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __unicode__(self):
        return unicode(self.pageblock())

    def needs_submit(self):
        return True

    @classmethod
    def add_form(self):
        return CalendarChartForm()

    def edit_form(self):
        return CalendarChartForm(instance=self)

    @classmethod
    def create(self, request):
        form = CalendarChartForm(request.POST)
        return form.save()

    def edit(self, vals, files):
        form = CalendarChartForm(data=vals,
                                 files=files,
                                 instance=self)
        if form.is_valid():
            form.save()

    def unlocked(self, user):
        return True


class CalendarChartForm(forms.ModelForm):
    class Meta:
        model = CalendarChart


class CalendarResponse(models.Model):
    conv_scen = models.ForeignKey(CalendarChart, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)
    first_click = models.ForeignKey(ConvClick,
                                    related_name="calendar_first_click",
                                    null=True, blank=True)
    last_click = models.ForeignKey(ConvClick,
                                   related_name="calendar_last_click",
                                   null=True, blank=True)


class DosageActivity(models.Model):
    pageblocks = generic.GenericRelation(PageBlock)
    template_file = "activities/dosageactivity.html"
    js_template_file = "activities/dosageactivity_js.html"
    css_template_file = "activities/dosageactivity_css.html"
    display_name = "Dosage Activity"
    explanation = models.TextField(default='')
    question = models.CharField(max_length=64)
    ml_nvp = models.IntegerField(default=0)
    times_day = models.IntegerField(default=0)
    weeks = models.IntegerField(default=0)

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __unicode__(self):
        return unicode(self.pageblock())

    def needs_submit(self):
        return True

    @classmethod
    def add_form(self):
        return DosageActivityForm()

    def edit_form(self):
        return DosageActivityForm(instance=self)

    @classmethod
    def create(self, request):
        form = DosageActivityForm(request.POST)
        return form.save()

    def edit(self, vals, files):
        form = DosageActivityForm(data=vals, files=files, instance=self)
        if form.is_valid():
            form.save()

    def submit(self, user, data):
        for k in data.keys():
            if k == "times_day":
                td = int(data[k])
            if k == 'mlnvp':
                ml = int(data[k])
            if k == 'weeks':
                wks = int(data[k])
        dr = DosageActivityResponse(dosage_activity=self,
                                    user=user, times_day=td,
                                    weeks=wks, ml_nvp=ml)
        dr.save()

    def redirect_to_self_on_submit(self):
        return True

    def unlocked(self, user):
        '''We want to make sure the user has filled out
        the appropriate fields before proceeding.'''
        response = DosageActivityResponse.objects.filter(
            dosage_activity=self, user=user)
        if (len(response) == 1
                and response[0].ml_nvp is not None
                and response[0].times_day is not None
                and response[0].weeks is not None):
            return True
        else:
            return False

    def clear_user_submissions(self, user):
        DosageActivityResponse.objects.filter(user=user,
                                              dosage_activity=
                                              self).delete()

    def dosage_response(self, user):
        try:
            response = DosageActivityResponse.objects.filter(
                dosage_activity=self, user=user)
            if response.count() > 0:
                return response[0]
            else:
                return None
        except DosageActivityResponse.DoesNotExist:
            return None


class DosageActivityForm(forms.ModelForm):
    class Meta:
        model = DosageActivity


class DosageActivityResponse(models.Model):
    dosage_activity = models.ForeignKey(DosageActivity,
                                        null=True, blank=True,
                                        related_name='dosage_resp')
    user = models.ForeignKey(User, null=True, blank=True)
    ml_nvp = models.IntegerField()
    times_day = models.IntegerField()
    weeks = models.IntegerField()
