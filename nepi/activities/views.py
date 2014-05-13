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


def add_conversation(request, pk):
    if request.method == 'POST':
        scenario = ConversationScenario.objects.get(pk=pk)
        form = ConversationForm(request.POST)
        if form.is_valid():
            nc = Conversation.objects.create()
            scenario = ConversationScenario.objects.get(pk=pk)
            nc.scenario_type = form.cleaned_data['scenario_type']
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
            return HttpResponseRedirect('/thanks/')  # Redirect after POST
    else:
        form = ConversationForm()  # An unbound form

    return render(request, 'activities/add_conversation.html', {
        'form': form,
    })


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
    success_url = '/thank_you/'


class UpdateConversationView(UpdateView):
    model = Conversation
    template_name = 'activities/update_conversation.html'
    fields = ['text_one', 'text_two', 'text_three', 'complete_dialog']
    success_url = '/thank_you/'


class DeleteConversationView(DeleteView):
    model = Conversation
    success_url = '../../../activities/classview_scenariolist/'


def get_click(request):
    if request.method == 'POST' and request.is_ajax():
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
