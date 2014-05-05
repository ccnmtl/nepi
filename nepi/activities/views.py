# Create your views here.
from annoying.decorators import render_to
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from pagetree.helpers import get_hierarchy
from django import forms
from nepi.activities.models import (
    ConversationScenario, Conversation)
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from nepi.activities.models import Conversation, ConversationScenario
from django.core.urlresolvers import reverse_lazy


class AjaxableResponseMixin(object):
    """
    Taken from Django site.
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return self.render_to_json_response(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return self.render_to_json_response(data)
        else:
            return response



def add_conversation(request, pk):
    class ConversationForm(forms.ModelForm):
        class Meta:
            model = Conversation
            fields = ['text_one','text_two','text_three','complete_dialog']
    if request.method == 'POST':
        scenario = ConversationScenario.objects.get(pk=pk)
        form = ConversationForm(request.POST)
        if form.is_valid():
            nc = Conversation.objects.create()
            nc.conv_scen = scenario
            nc.scenario = ConversationScenario.objects.get(pk=pk)
            nc.text_one = form.cleaned_data['text_one']
            nc.text_two = form.cleaned_data['text_two']
            nc.text_three = form.cleaned_data['text_three']
            nc.complete_dialog = form.cleaned_data['complete_dialog']
            nc.save()
            return HttpResponseRedirect('/thanks/')  # Redirect after POST
    else:
        form = ConversationForm()  # An unbound form

    return render(request, 'activities/add_conversation.html', {
        'form': form,
    })

def get_scenarios_and_conversations(request):
    scenarios = ConversationScenario.objects.all()
    conversations = Conversation.objects.all()
    return render(request, 'activities/scenario_list.html', {
        'scenarios': scenarios, 'conversations' : conversations
    })



class ScenarioListView(ListView, AjaxableResponseMixin):
    template_name = "activities/class_scenario_list_view.html"
    model = ConversationScenario

    def get_context_data(self, **kwargs):
        context = super(ScenarioListView, self).get_context_data(**kwargs)
        context['conversations'] = Conversation.objects.all()
        return context


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
    # this will hopefully become an Ajax function...
    # what sort of validation do I perform if there is no form?
    if request.is_ajax():
        rs, created = ConversationResponse.objects.get_or_create(conv_scen=self, user=request.user)
        course = Course(pk=self.object.pk, name=self.object.name,
                        startingBudget=self.object.startingBudget,
                        enableNarrative=self.object.enableNarrative,
                        message=self.object.message,
                        active=self.object.active)
        course.save()
        return self.render_to_json_response(course)
    else:
        return response
