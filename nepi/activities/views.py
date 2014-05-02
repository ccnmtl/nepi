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
from django.views.generic.edit import CreateView, UpdateView, DeleteView


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


class ConversationScenarioListView(ListView):
    template_name = "activities/scenario_list.html"
    model = ConversationScenario

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
    template_name = 'activities/add_conversation.html'
    success_url = '/thank_you/'


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
