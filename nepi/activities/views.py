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


# but I don't really need and ajax thanks view...
class ThanksView(AjaxableResponseMixin, View):
    '''We need a generic thanks view to pop up
    when appropriate and then refresh the page.'''
    def get(self, request):
        return render('thanks.html')


class CreateConverstionView(AjaxResponseMixin, CreateView):
    model = Conversation
    template_name = "activities/add_conversation.html"
    # do I need to list fields for ajax? even though form
    # is defined?
    fields = ["scenario_type", "text_one", "response_one",
              "response_two", "response_three", "response_four",
              "response_five", "response_six", "complete_dialog"]
    success_url = '/thank_you/'

    def from_valid(self, request, pk, form):
        response = super(CreateConverstionView, self).form_valid(form)
        if self.request.is_ajax():
            # request.pk? or self.pk? or just pk
            scenario = Scenario.objects.get(scenario=pk)

# 93     def form_valid(self, form):
# 94         response = super(, self).form_valid(form)
# 95         
# 96             course = Course(pk=self.object.pk, name=self.object.name,
# 97                             startingBudget=self.object.startingBudget,
# 98                             enableNarrative=self.object.enableNarrative,
# 99                             message=self.object.message,
# 100                             active=self.object.active)
# 101             course.save()
# 102             return self.render_to_json_response(course)
# 103         else:
# 104             return response

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
            nc.response_four = form.cleaned_data['response_four']
            nc.response_five = form.cleaned_data['response_five']
            nc.response_six = form.cleaned_data['response_six']
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


def get_last(request):
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
            elif cresp.first_click is not None and cresp.second_click is None:
                return render_to_json_response(
                    {'success': True, 'last_conv': cresp.first_click})

        except ConversationResponse.DoesNotExist:
            return render_to_json_response({'success': False})
