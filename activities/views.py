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


