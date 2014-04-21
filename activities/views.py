# Create your views here.
from annoying.decorators import render_to
from .models import Conversation#, Test
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from pagetree.helpers import get_hierarchy
import csv
from cStringIO import StringIO
from django.core.urlresolvers import reverse
from pagetree.generic.views import PageView, EditView
from django.views.generic.edit import CreateView, UpdateView
from activities.models import NurseConversation, PatientConversation
from activities.models import ConversationDialog, ConversationScenario
from activities.models import Conversation


class CreateNurseConversationView(CreateView):
    '''generic class based view for
    adding a school'''
    model = NurseConversation
    template_name = 'icap/add_school.html'
    success_url = '/thank_you/'


class UpdateNurseConversationView(UpdateView):
    '''generic class based view for
    editing a school'''
    model = NurseConversation
    template_name = 'icap/add_school.html'
    success_url = '/thank_you/'


class CreatePatientConversationView(CreateView):
    '''generic class based view for
    adding a school'''
    model = PatientConversation
    template_name = 'icap/add_school.html'
    success_url = '/thank_you/'


class UpdatePatientConversationView(UpdateView):
    '''generic class based view for
    editing a school'''
    model = PatientConversation
    template_name = 'icap/add_school.html'
    success_url = '/thank_you/'


class CreateConversationDialogView(CreateView):
    '''generic class based view for
    adding a school'''
    model = ConversationDialog
    template_name = 'icap/add_school.html'
    success_url = '/thank_you/'


class UpdateConversationDialogView(UpdateView):
    '''generic class based view for
    editing a school'''
    model = ConversationDialog
    template_name = 'icap/add_school.html'
    success_url = '/thank_you/'


class CreateConversationScenarioView(CreateView):
    '''generic class based view for
    adding a school'''
    model = ConversationScenario
    template_name = 'icap/add_school.html'
    success_url = '/thank_you/'


class UpdateConversationScenarioView(UpdateView):
    '''generic class based view for
    editing a school'''
    model = ConversationScenario
    template_name = 'icap/add_school.html'
    success_url = '/thank_you/'


class CreateConversationView(CreateView):
    '''generic class based view for
    adding a school'''
    model = Conversation
    template_name = 'icap/add_school.html'
    success_url = '/thank_you/'


class UpdateConversationView(UpdateView):
    '''generic class based view for
    editing a school'''
    model = Conversation
    template_name = 'icap/add_school.html'
    success_url = '/thank_you/'


class ViewPage(PageView):
    template_name = "main/conversation.html"
    hierarchy_name = "main"
    hierarchy_base = "/pages/main/"
    gated = False


class EditPage(EditView):
    template_name = "main/edit_page.html"
    hierarchy_name = "main"
    hierarchy_base = "/pages/main/"



@render_to('activities/conversation.html')
def conversation(request, id):
    conversation = get_object_or_404(Conversation, id=id)
    section = conversation.pageblock().section
    h = get_hierarchy()
    return dict(conversation=conversation, section=section,
                root=h.get_root())


@render_to('activities/edit_conversation.html')
def update_conversation(request, id):
    conversation = get_object_or_404(Lab, id=id)
    section = lab.pageblock().section
    h = get_hierarchy()
    return dict(conversation=conversation, section=section,
                root=h.get_root())

@render_to('activities/create_conversation.html')
def create_conversation(request):
    pass
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


