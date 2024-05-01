from __future__ import unicode_literals

from decimal import Decimal

from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models.query_utils import Q
from django.urls.base import reverse
from django.utils.encoding import smart_str
from pagetree.models import PageBlock
from pagetree.reports import ReportableInterface, ReportColumnInterface


CONV_CHOICES = (
    ('G', 'Good'),
    ('B', 'Bad'),
)


class Conversation(models.Model):
    scenario_type = models.CharField(max_length=1, choices=CONV_CHOICES,
                                     default='G')
    text_one = models.TextField(null=True, blank=True)
    response_one = models.TextField(null=True, blank=True)
    response_two = models.TextField(null=True, blank=True)
    response_three = models.TextField(null=True, blank=True)
    complete_dialog = models.TextField(null=True, blank=True)

    def __str__(self):
        return smart_str(self.scenario_type)

    def as_dict(self):
        return dict(
            scenario_type=self.scenario_type,
            text_one=self.text_one,
            response_one=self.response_one,
            response_two=self.response_two,
            response_three=self.response_three,
            complete_dialog=self.complete_dialog
        )

    @classmethod
    def create_from_dict(cls, d):
        return cls.objects.create(
            scenario_type=d.get('scenario_type', 'G'),
            text_one=d.get('text_one', ''),
            response_one=d.get('response_one', ''),
            response_two=d.get('response_two', ''),
            response_three=d.get('response_three', ''),
            complete_dialog=d.get('complete_dialog', '')
        )

    def get_scenario(self):
        if self.scenario_type == 'G':
            return self.good_conversation.first()
        else:
            return self.bad_conversation.first()


class ConversationScenario(models.Model):
    pageblocks = GenericRelation(PageBlock)
    description = models.TextField(blank=True)
    display_name = "Conversation Scenario"
    template_file = "activities/conversation.html"
    js_template_file = "activities/conversation_js.html"
    css_template_file = "activities/conversation_css.html"
    exportable = False
    importable = False
    good_conversation = models.ForeignKey(Conversation, null=True, blank=True,
                                          related_name='good_conversation',
                                          on_delete=models.CASCADE)
    bad_conversation = models.ForeignKey(Conversation, null=True, blank=True,
                                         related_name='bad_conversation',
                                         on_delete=models.CASCADE)

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __str__(self):
        return smart_str(self.pageblock())

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

    def edit_form_alt_text(self):
        alt_text = ''
        if self.good_conversation:
            url = reverse("update_conversation",
                          args=[self.good_conversation.id])
            alt_text += "<a href=\"" + url + \
                "\">update good conversation</a><br />"
        else:
            url = reverse("create_conversation", args=[self.id, 'G'])
            alt_text += "<a href=\"" + url + \
                "\">add good conversation</a><br />"

        if self.bad_conversation:
            url = reverse("update_conversation",
                          args=[self.bad_conversation.id])

            alt_text += "<a href=\"" + url + "\">update bad conversation</a>"
        else:
            url = reverse("create_conversation", args=[self.id, 'B'])
            alt_text += "<a href=\"" + url + "\">add bad conversation</a>"
        return alt_text

    def edit_form(self):
        class EditForm(forms.Form):
            description = forms.CharField(initial=self.description)
            alt_text = self.edit_form_alt_text()
        return EditForm()

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
        return False

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
        responses = ConversationResponse.objects.filter(
            conv_scen=self, user=user)

        if responses.count() > 0:
            response = responses.first()
            if response.third_click is not None:
                return response.third_click.conversation.scenario_type
            elif response.second_click is not None:
                return response.second_click.conversation.scenario_type
            elif response.first_click is not None:
                return response.first_click.conversation.scenario_type

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

    @classmethod
    def create_from_dict(cls, d):
        good = d.get('good_conversation', {})
        bad = d.get('bad_conversation', {})

        return cls.objects.create(
            description=d.get('description', ''),
            good_conversation=Conversation.create_from_dict(good),
            bad_conversation=Conversation.create_from_dict(bad)
        )

    def as_dict(self):
        d = dict(description=self.description)
        if self.good_conversation:
            d['good_conversation'] = self.good_conversation.as_dict()
        if self.bad_conversation:
            d['bad_conversation'] = self.bad_conversation.as_dict()
        return d


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


class ConversationForm(forms.ModelForm):
    class Meta:
        model = Conversation
        exclude = []


class ConversationScenarioForm(forms.ModelForm):
    class Meta:
        model = ConversationScenario
        exclude = ('good_conversation', 'bad_conversation',)


class ConvClick(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    conversation = models.ForeignKey(
        Conversation, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return "%s Click" % self.conversation.scenario_type


class ConversationResponse(models.Model):
    conv_scen = models.ForeignKey(
        ConversationScenario, null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE)
    first_click = models.ForeignKey(
        ConvClick, related_name="first_click", null=True, blank=True,
        on_delete=models.CASCADE)
    second_click = models.ForeignKey(
        ConvClick, related_name="second_click", null=True, blank=True,
        on_delete=models.CASCADE)
    third_click = models.ForeignKey(
        ConvClick, related_name="third_click",
        null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return "Response to %s" % self.conv_scen


class ImageInteractive(models.Model):
    pageblocks = GenericRelation(PageBlock)
    template_file = "activities/imagemapchart.html"
    js_template_file = "activities/imagemapchart_js.html"
    css_template_file = "activities/imagemapchart_css.html"
    display_name = "Image Interactive"
    intro_text = models.TextField(default='')

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __str__(self):
        return smart_str(self.pageblock())

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

    @classmethod
    def create_from_dict(cls, d):
        return cls.objects.create(intro_text=d.get('intro_text', ''))

    def as_dict(self):
        return dict(intro_text=self.intro_text)


class ImageInteractiveForm(forms.ModelForm):
    class Meta:
        model = ImageInteractive
        exclude = []


class ARTCard(models.Model):
    pageblocks = GenericRelation(PageBlock)
    template_file = "activities/artcard.html"
    js_template_file = "activities/artcard_js.html"
    css_template_file = "activities/artcard_css.html"
    display_name = "ART Card"
    intro_text = models.TextField(default='')

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __str__(self):
        return smart_str(self.pageblock())

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

    @classmethod
    def create_from_dict(cls, d):
        return cls.objects.create(intro_text=d.get('intro_text', ''))

    def as_dict(self):
        return dict(intro_text=self.intro_text)


class ARTCardForm(forms.ModelForm):
    class Meta:
        model = ARTCard
        exclude = []


class AdherenceCard(models.Model):
    pageblocks = GenericRelation(PageBlock)
    template_file = "activities/adherencecard.html"
    quiz_class = models.TextField()
    display_name = "Adherence Card"

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __str__(self):
        return smart_str(self.pageblock())

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

    @classmethod
    def create_from_dict(cls, d):
        return cls.objects.create(quiz_class=d.get('quiz_class', ''))

    def as_dict(self):
        return dict(quiz_class=self.quiz_class)


class AdherenceCardForm(forms.ModelForm):
    class Meta:
        model = AdherenceCard
        exclude = []


class RetentionRateCard(models.Model):
    pageblocks = GenericRelation(PageBlock)
    template_file = "activities/retentionrate.html"
    js_template_file = "activities/retentionrate_js.html"
    css_template_file = "activities/retentionrate_css.html"
    display_name = "Retention Rate Card"
    intro_text = models.TextField(default='')

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __str__(self):
        return smart_str(self.pageblock())

    def needs_submit(self):
        return True

    @classmethod
    def add_form(self):
        return RetentionRateCardForm()

    def edit_form(self):
        return RetentionRateCardForm(instance=self)

    def clear_user_submissions(self, user):
        RetentionResponse.objects.filter(
            user=user, retentionrate=self).delete()

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
            retentionrate=self, user=user)
        if (len(response) == 1 and
            response[0].cohort_click is not None and
            response[0].start_date_click is not None and
            response[0].eligible_click is not None and
            response[0].delivery_date_click is not None and
                response[0].follow_up_click is not None):
            return True
        else:
            return False

    @classmethod
    def create_from_dict(cls, d):
        return cls.objects.create(intro_text=d.get('intro_text', ''))

    def as_dict(self):
        return dict(intro_text=self.intro_text)


class RetentionRateCardForm(forms.ModelForm):
    class Meta:
        model = RetentionRateCard
        exclude = []


class RetentionClick(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    click_string = models.CharField(max_length=50)

    def __str__(self):
        return smart_str(self.click_string)


class RetentionResponse(models.Model):
    retentionrate = models.ForeignKey(
        RetentionRateCard, null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE)
    cohort_click = models.ForeignKey(
        RetentionClick, related_name="retention_cohort_click",
        null=True, blank=True, on_delete=models.CASCADE)
    start_date_click = models.ForeignKey(
        RetentionClick,
        related_name="retention_start_date_click",
        null=True, blank=True, on_delete=models.CASCADE)
    eligible_click = models.ForeignKey(
        RetentionClick,
        related_name="retention_eligible_click",
        null=True, blank=True, on_delete=models.CASCADE)
    delivery_date_click = models.ForeignKey(
        RetentionClick,
        related_name="retention_delivery_date_click",
        null=True, blank=True, on_delete=models.CASCADE)
    follow_up_click = models.ForeignKey(
        RetentionClick,
        related_name="retention_follow_up_click",
        null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return ("Response to " + str(self.retentionrate))


class Month(models.Model):
    display_name = models.CharField(max_length=255, default="")

    def month_name(self):
        return self.display_name.split(' ')[0]

    def __str__(self):
        hierarchy_name = None
        chart = self.calendarchart_set.first()
        if chart:
            hierarchy_name = chart.pageblock().section.hierarchy.name
        return "%s in %s" % (self.display_name, hierarchy_name)

    @classmethod
    def create_from_dict(cls, d):
        month = cls.objects.create(display_name=d.get('display_name', ''))

        for day in d['days']:
            day['month'] = month
            month.day_set.add(Day.create_from_dict(day))
        return month

    def as_dict(self):
        d = dict(display_name=self.display_name)
        d['days'] = []
        for day in self.day_set.all():
            d['days'].append(day.as_dict())
        return d


class Day(models.Model):
    calendar = models.ForeignKey(Month, on_delete=models.CASCADE)
    number = models.IntegerField(default=1)
    explanation = models.TextField(default="")

    class Meta:
        ordering = ['number']

    def __str__(self):
        return "%s %s" % (self.number, self.explanation)

    @classmethod
    def create_from_dict(cls, d):
        return cls.objects.create(
            number=d.get('number', 1),
            explanation=d.get('explanation', ''),
            calendar=d.get('month', None)
        )

    def as_dict(self):
        return dict(
            explanation=self.explanation,
            number=self.number
        )


class CalendarChart(models.Model):
    pageblocks = GenericRelation(PageBlock)
    template_file = "activities/calendarchart.html"
    js_template_file = "activities/calendarchart_js.html"
    css_template_file = "activities/calendarchart_css.html"
    display_name = "Calendar Chart"
    month = models.ForeignKey(Month, on_delete=models.CASCADE)
    description = models.TextField(default='')
    correct_date = models.IntegerField(default=1)

    def pageblock(self):
        return self.pageblocks.all()[0]

    def __str__(self):
        return smart_str(self.pageblock())

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

    @classmethod
    def create_from_dict(cls, d):
        return cls.objects.create(
            description=d.get('description', ''),
            correct_date=d.get('correct_date', ''),
            month=Month.create_from_dict(d.get('month', {}))
        )

    def as_dict(self):
        d = dict(
            description=self.description,
            correct_date=self.correct_date,
            month=self.month.as_dict()
        )
        return d


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
        exclude = []


class CalendarResponse(models.Model):
    calendar_activity = models.ForeignKey(
        CalendarChart, null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE)
    first_click = models.ForeignKey(
        Day, null=True, blank=True,
        related_name="first_click", on_delete=models.CASCADE)
    correct_click = models.ForeignKey(
        Day, null=True, blank=True,
        related_name="correct_click", on_delete=models.CASCADE)


class DosageActivity(models.Model):
    pageblocks = GenericRelation(PageBlock)
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

    def __str__(self):
        return smart_str(self.pageblock())

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
        if (len(response) == 1 and
            response[0].ml_nvp is not None and
            response[0].times_day is not None and
                response[0].weeks is not None):
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

    def as_dict(self):
        return dict(
            explanation=self.explanation,
            question=self.question,
            ml_nvp=str(self.ml_nvp),
            times_day=self.times_day,
            weeks=self.weeks)

    @classmethod
    def create_from_dict(cls, d):
        return cls.objects.create(
            explanation=d.get('explanation', None),
            question=d.get('question', None),
            ml_nvp=Decimal(d.get('ml_nvp', 0.0)),
            times_day=d.get('times_day', 0),
            weeks=d.get('weeks', 0)
        )


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
        exclude = []


class DosageActivityResponse(models.Model):
    dosage_activity = models.ForeignKey(
        DosageActivity, null=True, blank=True,
        related_name='dosage_resp', on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE)
    ml_nvp = models.DecimalField(default=0.0, max_digits=4, decimal_places=2)
    times_day = models.IntegerField()
    weeks = models.IntegerField()


ReportableInterface.register(ConversationScenario)
ReportableInterface.register(CalendarChart)
ReportableInterface.register(DosageActivity)
