from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from nepi.activities.models import Conversation, ConversationScenario, \
    ConvClick, ConversationResponse, ConversationForm, RetentionRateCard, \
    RetentionClick, RetentionResponse
from nepi.mixins import JSONResponseMixin
import json


class CreateConverstionView(CreateView):
    template_name = 'activities/add_conversation.html'
    form_class = ConversationForm
    fields = ['text_one', 'response_one',
              'response_two', 'response_three', 'complete_dialog']
    success_url = '/pages/main/edit/'

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
        return HttpResponseRedirect('/pages/main/edit/')


def render_to_json_response(context, **response_kwargs):
    data = json.dumps(context)
    response_kwargs['content_type'] = 'application/json'
    return HttpResponse(data, **response_kwargs)


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
    success_url = '/pages/main/edit/'


class UpdateConversationView(UpdateView):
    model = Conversation
    template_name = 'activities/add_conversation.html'
    fields = ['text_one', 'response_one',
              'response_two', 'response_three',
              'complete_dialog']
    success_url = '/pages/main/edit/'


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
        rs, created = ConversationResponse.objects.get_or_create(
            conv_scen=scenario, user=request.user)
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
        return render_to_json_response({'success': True})


class LastResponse(View, JSONResponseMixin):
    '''Should this be a create view?'''
    def post(self, request):
        scenario = get_object_or_404(ConversationScenario,
                                     pk=request.POST['scenario'])
        try:
            cresp = ConversationResponse.objects.get(
                user=request.user, conv_scen=scenario)
            if cresp.third_click is not None:
                return render_to_json_response(
                    {'success': True,
                     'last_conv':
                     cresp.third_click.conversation.scenario_type})
            elif (cresp.first_click is not None
                  and cresp.second_click is None):
                    return render_to_json_response(
                        {'success': True,
                         'last_conv':
                         cresp.first_click.conversation.scenario_type})

        except ConversationResponse.DoesNotExist:
            return render_to_json_response({'success': False})


class CreateCalendar(CreateView):
    model = Conversation
    template_name = 'activities/add_conversation.html'
    success_url = '/pages/main/edit/'


class SaveRetentionResponse(View, JSONResponseMixin):
    '''There must be a way to make a simple short generic method'''

    def compare_strings(self, retresponse, click_string, click_reference):
        click_saved = getattr(retresponse, click_string)
        if click_saved is None:
            retresponse.click_saved = click_reference
            retresponse.click_saved.save()
            click_reference.save()
            return render_to_json_response({'success': True})
        elif click_saved is not None:
            '''We can assume that this attribute already has a value'''
            return render_to_json_response({'success': True})

    def post(self, request):
        acceptable_clicks = ["cohort_click", "start_date_click",
                             "eligible_click", "delivery_date_click",
                             "dec_click", "jan_click", "feb_click",
                             "mar_click", "apr_click", "may_click",
                             "jun_click"]
        retention = get_object_or_404(RetentionRateCard,
                                      pk=request.POST['retention_id'])
        click_string = request.POST['click_string']
        if click_string in acceptable_clicks:
            retentionclick = RetentionClick.objects.create(
                click_string=click_string)
            rr, created = RetentionResponse.objects.get_or_create(
                retentionrate=retention, user=request.user)
            return self.compare_strings(rr, click_string, retentionclick)
        else:
            '''If submitted string is not in the acceptable strings list
            something is very funny.'''
            return render_to_json_response({'success': False})
