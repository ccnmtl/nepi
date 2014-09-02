from datetime import datetime
from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.query_utils import Q
from pagetree.models import PageBlock
from pagetree.reports import ReportableInterface, ReportColumnInterface


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

    def clear_user_submissions(self, user):
        ConversationResponse.objects.filter(user=user, conv_scen=self).delete()

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
        qs = ConversationResponse.objects.filter(conv_scen=self, user=user)

        good = qs.filter(Q(first_click__conversation=self.good_conversation) |
                         Q(second_click__conversation=self.good_conversation) |
                         Q(third_click__conversation=self.good_conversation))
        bad = qs.filter(Q(first_click__conversation=self.bad_conversation) |
                        Q(second_click__conversation=self.bad_conversation) |
                        Q(third_click__conversation=self.bad_conversation))
        return good.count() > 0 and bad.count() > 0

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
            else:
                return 0
        except ConversationResponse.DoesNotExist:
            return 0

    def report_metadata(self):
        return [ConversationReportColumn(self.pageblock(),
                                         self.good_conversation),
                ConversationReportColumn(self.pageblock(),
                                         self.bad_conversation)]

    def report_values(self):
        return [ConversationReportColumn(self.pageblock())]

    def score(self, user):
        if not self.unlocked(user):
            return None  # incomplete

        responses = ConversationResponse.objects.filter(
            conv_scen=self, user=user,
            first_click__conversation=self.good_conversation)

        if responses.count() > 0:
            return 1
        else:
            return 0


class ConversationReportColumn(ReportColumnInterface):

    def __init__(self, pageblock, conversation=None):
        self.hierarchy = pageblock.section.hierarchy
        self.section = pageblock.section
        self.conversation = conversation
        self.pageblock_id = pageblock.block().id

    def identifier(self):
        return "%s_%s_conversation" % (self.hierarchy.id, self.pageblock_id)

    def metadata(self):
        row = [self.hierarchy.name,
               self.identifier(),
               self.section.label,
               "Conversation Activity single choice"]
        if self.conversation:
            row.append(self.conversation.id)
            row.append(self.conversation.scenario_type)
        return row

    def user_value(self, user):
        response = ConversationResponse.objects.filter(
            user=user, conv_scen__id=self.pageblock_id)
        if response.count() == 0:
            return None
        else:
            return response[0].first_click.conversation.id


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

    def __unicode__(self):
        return "%s Click" % self.conversation.scenario_type


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
        return "Response to %s" % self.conv_scen


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


class AdherenceCard(models.Model):
    pageblocks = generic.GenericRelation(PageBlock)
    template_file = "activities/adherencecard.html"
    quiz_class = models.TextField()
    display_name = "Adherence Card"

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __unicode__(self):
        return unicode(self.pageblock())

    def needs_submit(self):
        return False

    @classmethod
    def add_form(self):
        return AdherenceCardForm()

    def edit_form(self):
        return AdherenceCardForm(instance=self)

    @classmethod
    def create(self, request):
        form = AdherenceCardForm(request.POST)
        return form.save()

    def edit(self, vals, files):
        form = AdherenceCardForm(data=vals, files=files, instance=self)
        if form.is_valid():
            form.save()

    def unlocked(self, user):
        return True


class AdherenceCardForm(forms.ModelForm):
    class Meta:
        model = AdherenceCard


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

    def __unicode__(self):
        return("Click String: " + str(self.click_string))


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


class Month(models.Model):
    display_name = models.CharField(max_length=255, default="")

    def month_name(self):
        return self.display_name.split(' ')[0]

    def __unicode__(self):
        return"%s" % self.display_name


class CalendarChart(models.Model):
    pageblocks = generic.GenericRelation(PageBlock)
    template_file = "activities/calendarchart.html"
    js_template_file = "activities/calendarchart_js.html"
    css_template_file = "activities/calendarchart_css.html"
    display_name = "Calendar Chart"
    month = models.ForeignKey(Month)
    description = models.TextField(default='')
    correct_date = models.IntegerField(default=1)

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
        '''Make sure the user has selected the correct
        date before they can proceed.'''
        responses = CalendarResponse.objects.filter(
            calendar_activity=self, user=user,
            correct_click__number=self.correct_date)

        return responses.count() > 0

    def submit(self, user, data):
        for k in data.keys():
            if k == "day":
                day = int(data[k])
            try:
                cr = CalendarResponse.objects.get(calendar_activity=self,
                                                  user=user)
                if cr.first_click is None:
                    cr.first_click = day
                if cr.day == self.correct_date:
                    cr.correct_click = cr.day
                cr.save()
            except CalendarResponse.DoesNotExist:
                return None

    def redirect_to_self_on_submit(self):
        return True

    def report_metadata(self):
        '''meta data is for key table?'''
        return [CalendarReportColumn(self.pageblock(), self.correct_date)]

    def report_values(self):
        return [CalendarReportColumn(self.pageblock(), self.correct_date)]

    def score(self, user):
        if not self.unlocked(user):
            return None

        responses = CalendarResponse.objects.filter(
            user=user, calendar_activity=self,
            first_click__number=self.correct_date)

        if responses.count() > 0:
            return 1
        else:
            return 0

    def clear_user_submissions(self, user):
        CalendarResponse.objects.filter(calendar_activity=self,
                                        user=user).delete()


class CalendarReportColumn(ReportColumnInterface):

    def __init__(self, pageblock, correct_date):
        self.hierarchy = pageblock.section.hierarchy
        self.section = pageblock.section
        self.pageblock_id = pageblock.block().id
        self.correct_date = correct_date

    def identifier(self):
        return "%s_%s_calendar" % (self.hierarchy.id, self.pageblock_id)

    def metadata(self):
        row = [self.hierarchy.name,
               self.identifier(),
               self.section.label,
               "Appointment Scheduling boolean"]
        return row

    def user_value(self, user):
        response = CalendarResponse.objects.filter(
            user=user, calendar_activity__id=self.pageblock_id)
        if response.count() == 0:
            return None
        else:
            return response[0].first_click.number == self.correct_date


class CalendarChartForm(forms.ModelForm):
    class Meta:
        model = CalendarChart


class Day(models.Model):
    calendar = models.ForeignKey(Month)
    number = models.IntegerField(default=1)
    explanation = models.CharField(max_length=255, default="")

    def __unicode__(self):
        return"%s %s" % (self.number, self.explanation)


class CalendarResponse(models.Model):
    calendar_activity = models.ForeignKey(CalendarChart, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)
    first_click = models.ForeignKey(Day, null=True, blank=True,
                                    related_name="first_click")
    correct_click = models.ForeignKey(Day, null=True, blank=True,
                                      related_name="correct_click")


class DosageActivity(models.Model):
    pageblocks = generic.GenericRelation(PageBlock)
    template_file = "activities/dosageactivity.html"
    js_template_file = "activities/dosageactivity_js.html"
    css_template_file = "activities/dosageactivity_css.html"
    display_name = "Dosage Activity"
    explanation = models.TextField()
    question = models.TextField()
    ml_nvp = models.DecimalField(default=0.0, max_digits=4, decimal_places=2)
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
        td = int(data["times_day"])
        ml = float(data['mlnvp'])
        wks = int(data['weeks'])
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
                                              dosage_activity=self).delete()

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

    def report_metadata(self):
        return [DosageReportColumn(self.pageblock(), "ml_nvp"),
                DosageReportColumn(self.pageblock(), "times_day"),
                DosageReportColumn(self.pageblock(), "weeks")]

    def report_values(self):
        return [DosageReportColumn(self.pageblock(), "ml_nvp"),
                DosageReportColumn(self.pageblock(), "times_day"),
                DosageReportColumn(self.pageblock(), "weeks")]

    def score(self, user):
        response = DosageActivityResponse.objects.filter(
            user=user, dosage_activity=self)
        if response.count() == 0:
            return None
        elif (float(response[0].ml_nvp) == float(self.ml_nvp) and
              response[0].times_day == self.times_day and
                response[0].weeks == self.weeks):
            return 1
        else:
            return 0


class DosageReportColumn(ReportColumnInterface):

    def __init__(self, pageblock, field_name):
        self.hierarchy = pageblock.section.hierarchy
        self.section = pageblock.section
        self.pageblock_id = pageblock.block().id
        self.field_name = field_name

    def identifier(self):
        return "%s_%s_dosage" % (self.hierarchy.id, self.pageblock_id)

    def metadata(self):
        row = [self.hierarchy.name,
               self.identifier(),
               self.section.label,
               "Dosage Activity %s short text" % self.field_name]
        return row

    def user_value(self, user):
        response = DosageActivityResponse.objects.filter(
            user=user, dosage_activity__id=self.pageblock_id)
        if response.count() == 0:
            return None
        else:
            return getattr(response[0], self.field_name)


class DosageActivityForm(forms.ModelForm):
    class Meta:
        model = DosageActivity


class DosageActivityResponse(models.Model):
    dosage_activity = models.ForeignKey(DosageActivity,
                                        null=True, blank=True,
                                        related_name='dosage_resp')
    user = models.ForeignKey(User, null=True, blank=True)
    ml_nvp = models.DecimalField(default=0.0, max_digits=4, decimal_places=2)
    times_day = models.IntegerField()
    weeks = models.IntegerField()


ReportableInterface.register(ConversationScenario)
ReportableInterface.register(CalendarChart)
ReportableInterface.register(DosageActivity)
