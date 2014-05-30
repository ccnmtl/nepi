    # Create your views here.
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.http import HttpResponseRedirect
from django.shortcuts import render
import json
from nepi.activities.models import (
    Conversation, ConversationScenario,
    ConvClick, ConversationResponse,
    ConversationForm)
from nepi.main.views import AjaxableResponseMixin
from django.views.generic import View


# but I don't really need and ajax thanks view...
class ThanksView(AjaxableResponseMixin, View):
    '''We need a generic thanks view to pop up
    when appropriate and then refresh the page.'''
    def get(self, request):
        return render('thanks.html')


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


class SaveResponse(View):
    def post(self, request):
        if request.is_ajax():
            scenario = ConversationScenario.objects.get(
                pk=request.POST['scenario'])
            conversation = Conversation.objects.get(
                pk=request.POST['conversation'])
            conclick = ConvClick.objects.create(conversation=conversation)
            conclick.save()
            current_user = User.objects.get(pk=request.user.pk)
            rs, created = ConversationResponse.objects.get_or_create(
                conv_scen=scenario, user=current_user)
            rs.save()
            if rs.first_click is None:
                conclick.save()
                rs.first_click = conclick
                rs.save()
            if rs.first_click is not None and rs.second_click is None:
                conclick.save()
                rs.second_click = conclick
                rs.third_click = conclick
                rs.save()
            if rs.second_click is not None:
                conclick.save()
                rs.third_click = conclick
                rs.save()
            return render_to_json_response({'success': True})
        else:
            return render_to_json_response({'success': False})


class LastResponse(View):
    def post(request):
        if request.method == 'POST' and request.is_ajax():
            scenario = ConversationScenario.objects.get(
                pk=request.POST['scenario'])
            user = User.objects.get(pk=request.user.pk)
            try:
                cresp = ConversationResponse.objects.get(
                    user=user, scenario=scenario)
                if cresp.third_click is not None:
                    return render_to_json_response(
                        {'success': True, 'last_conv': cresp.third_click})
                elif (cresp.first_click is not None
                      and cresp.second_click is None):
                        return render_to_json_response(
                            {'success': True, 'last_conv': cresp.first_click})

            except ConversationResponse.DoesNotExist:
                return render_to_json_response({'success': False})


class CreateCalendar(CreateView):
    model = Conversation
    template_name = 'activities/add_conversation.html'
    success_url = '/pages/main/edit/'
