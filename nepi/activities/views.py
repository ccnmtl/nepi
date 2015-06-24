from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from pagetree.models import UserPageVisit

from nepi.activities.models import Conversation, ConversationScenario, \
    ConvClick, ConversationResponse, ConversationForm, RetentionRateCard, \
    RetentionClick, RetentionResponse, CalendarResponse, CalendarChart, Day
from nepi.mixins import JSONResponseMixin


class CreateConverstionView(CreateView):
    template_name = 'activities/add_conversation.html'
    form_class = ConversationForm
    fields = ['text_one', 'response_one',
              'response_two', 'response_three', 'complete_dialog']
    success_url = '/pages/optionb/en/edit/'

    def form_valid(self, form):
        nc = Conversation.objects.create()
        nc.scenario_type = form.cleaned_data['scenario_type']
        path_split = self.request.path.split('/')
        key = path_split[3]
        scenario = ConversationScenario.objects.get(pk=key)
        if nc.scenario_type == 'G':
            scenario.good_conversation = nc
            scenario.save()
        elif nc.scenario_type == 'B':
            scenario.bad_conversation = nc
            scenario.save()

        nc.text_one = form.cleaned_data['text_one']
        nc.response_one = form.cleaned_data['response_one']
        nc.response_two = form.cleaned_data['response_two']
        nc.response_three = form.cleaned_data['response_three']
        nc.complete_dialog = form.cleaned_data['complete_dialog']
        nc.save()
        return HttpResponseRedirect('/pages/optionb/en/edit/')


class ScenarioListView(ListView):
    template_name = "activities/class_scenario_list_view.html"
    model = ConversationScenario


class ScenarioDetailView(DetailView):
    template_name = "activities/class_scenario_list_view.html"
    model = ConversationScenario


class ScenarioDeleteView(DeleteView):
    model = ConversationScenario
    success_url = '../../../activities/classview_scenariolist/'


class CreateConversationView(CreateView):
    model = Conversation
    template_name = 'activities/add_conversation.html'
    success_url = '/pages/optionb/en/edit/'


class UpdateConversationView(UpdateView):
    model = Conversation
    template_name = 'activities/add_conversation.html'
    fields = ['text_one', 'response_one',
              'response_two', 'response_three',
              'complete_dialog']
    success_url = '/pages/optionb/en/edit/'


class DeleteConversationView(DeleteView):
    model = Conversation
    success_url = '../../../activities/classview_scenariolist/'


class SaveResponse(View, JSONResponseMixin):
    def post(self, request):
        scenario = get_object_or_404(ConversationScenario,
                                     pk=request.POST['scenario'])
        conversation = get_object_or_404(Conversation,
                                         pk=request.POST['conversation'])
        conclick = ConvClick.objects.create(conversation=conversation)
        conclick.save()

        responses = ConversationResponse.objects.filter(conv_scen=scenario,
                                                        user=request.user)
        if responses.count() > 0:
            rs = responses.first()
        else:
            rs = ConversationResponse.objects.create(conv_scen=scenario,
                                                     user=request.user)

        if rs.first_click is None:
            rs.first_click = conclick
            rs.save()
        elif rs.first_click is not None and rs.second_click is None:
            rs.second_click = conclick
            rs.third_click = conclick
            rs.save()
        elif rs.second_click is not None:
            rs.third_click = conclick
            rs.save()

        if scenario.unlocked(request.user):
            upv = UserPageVisit.objects.get(
                user=request.user,
                section=scenario.pageblock().section)
            upv.status = 'complete'
            upv.save()

        return self.render_to_json_response({'success': True})


class LastResponse(View, JSONResponseMixin):
    '''Should this be a create view?'''
    def post(self, request):
        scenario = get_object_or_404(ConversationScenario,
                                     pk=request.POST['scenario'])
        try:
            cresp = ConversationResponse.objects.get(
                user=request.user, conv_scen=scenario)
            if cresp.third_click is not None:
                return self.render_to_json_response(
                    {'success': True,
                     'last_conv':
                     cresp.third_click.conversation.scenario_type})
            elif (cresp.first_click is not None and
                  cresp.second_click is None):
                    return self.render_to_json_response(
                        {'success': True,
                         'last_conv':
                         cresp.first_click.conversation.scenario_type})

        except ConversationResponse.DoesNotExist:
            return self.render_to_json_response({'success': False})


class SaveRetentionResponse(View, JSONResponseMixin):
    '''There must be a way to make a simple short generic method'''

    acceptable_clicks = ["cohort_click", "start_date_click",
                         "eligible_click", "delivery_date_click",
                         "follow_up_click"]

    def get_user_response(self, block, user):
        response = RetentionResponse.objects.filter(
            retentionrate=block, user=user).first()
        if response is None:
            response = RetentionResponse.objects.create(
                retentionrate=block, user=user)
        return response

    def post(self, request):
        block_id = request.POST.get('retention_id', None)
        block = get_object_or_404(RetentionRateCard, pk=block_id)

        click_string = request.POST.get('click_string', '')
        if click_string in self.acceptable_clicks:
            rr = self.get_user_response(block, request.user)

            if getattr(rr, click_string) is None:
                clk = RetentionClick.objects.create(click_string=click_string)
                setattr(rr, click_string, clk)
                rr.save()

            is_done = block.unlocked(user=request.user)
            if is_done:
                upv, created = UserPageVisit.objects.get_or_create(
                    user=request.user,
                    section=block.pageblock().section)
                upv.status = 'complete'
                upv.save()

            return self.render_to_json_response({'success': True,
                                                 'done': is_done})
        else:
            '''If submitted string is not in the acceptable strings list
            something is very funny.'''
            return self.render_to_json_response({'success': False})


class SaveCalendarResponse(View, JSONResponseMixin):
    def post(self, request):
        calendar = get_object_or_404(CalendarChart,
                                     pk=request.POST['calendar'])
        day = get_object_or_404(Day,
                                pk=request.POST['day'])
        cr, created = CalendarResponse.objects.get_or_create(
            calendar_activity=calendar, user=request.user)
        if cr.first_click is None:
            cr.first_click = day
            cr.save()
        if day.number == calendar.correct_date:
            cr.correct_click = day
            cr.save()

        if calendar.unlocked(request.user):
            upv = UserPageVisit.objects.get(
                user=request.user,
                section=calendar.pageblock().section)
            upv.status = 'complete'
            upv.save()

        return self.render_to_json_response({'success': True})
