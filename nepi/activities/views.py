# Create your views here.
from annoying.decorators import render_to
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from pagetree.helpers import get_hierarchy
import csv
from cStringIO import StringIO
from django import forms
from django.core.urlresolvers import reverse
from pagetree.generic.views import PageView, EditView
from django.views.generic.edit import CreateView, UpdateView
from nepi.activities.models import ConversationScenario
from nepi.activities.models import Conversation
from nepi.activities.models import ConversationForm
from django.shortcuts import render

def add_conversation(request, pk):
    if request.method == 'POST':
        print "pk from url is " + pk
        scenario = ConversationScenario.objects.get(pk=pk)
        print "scenario pk is " + str(scenario.pk)
        form = ConversationForm(request.POST)
        if form.is_valid():
            nc = Conversation.objects.create()
            print "Type of scenario is " + str(type(scenario))
            nc.conv_scen=scenario
            nc.scenario=ConversationScenario.objects.get(pk=pk)
            print "conversation now thinks its scenorio is " + str(nc.conv_scen)
            print "conversation now thinks its scenorio pk is " + str(nc.conv_scen.pk)
            nc.text_one = form.cleaned_data['text_one']
            nc.text_two = form.cleaned_data['text_two']
            nc.text_three = form.cleaned_data['text_three']
            nc.complete_dialog = form.cleaned_data['complete_dialog']
            nc.save()
            return HttpResponseRedirect('/thanks/') # Redirect after POST
    else:
        form = ConversationForm() # An unbound form


    return render(request, 'activities/add_conversation.html', {
        'form': form,
    })


#class CreateConversationScenarioView(CreateView):
#    #seems to provide drop down interface to select existing fields
#    '''generic class based view for
#    adding a school'''
#    model = ConversationScenario
#    template_name = 'icap/add_nconversation.html'
#    success_url = '/thank_you/'


@render_to('activities/conversation.html')
def conversation(request, id):
    conversation = get_object_or_404(Conversation, id=id)
    section = conversation.pageblock().section
    h = get_hierarchy()
    return dict(conversation=conversation, section=section,
                root=h.get_root())


@render_to('activities/edit_conversation.html')
def edit_conversation(request, id):
    conversation = get_object_or_404(Lab, id=id)
    section = lab.pageblock().section
    h = get_hierarchy()
    return dict(conversation=conversation, section=section,
                root=h.get_root())

#@render_to('activities/create_conversation.html')
#def create_conversation(request):
#    pass
#    conversation = get_object_or_404(Lab, id=id)
#    section = lab.pageblock().section
#    h = get_hierarchy()
#    return dict(conversation=conversation, section=section,
#                root=h.get_root())


def delete_conversation(request, id):
    pass
#    converstaion = get_object_or_404(Test, id=id)
#    if request.method == "POST":
#        lab = test.lab
#        test.delete()
#        return HttpResponseRedirect(
#            reverse("edit-lab", args=[lab.id]))
#    return HttpResponse("""
#<html><body><form action="." method="post">Are you Sure?
#<input type="submit" value="Yes, delete it" /></form></body></html>
#""")
