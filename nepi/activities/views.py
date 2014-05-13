# Create your views here.
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
import json
from nepi.activities.models import (
    Conversation, ConversationScenario, ConvClick, ConversationResponse)


def render_to_json_response(context, **response_kwargs):
    data = json.dumps(context)
    response_kwargs['content_type'] = 'application/json'
    return HttpResponse(data, **response_kwargs)


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


class ScenarioListView(ListView, AjaxableResponseMixin):
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


    # what sort of validation do I perform if there is no form?
def get_click(request):
    #response = super(AjaxableResponseMixin, self).form_valid(form)
    if request.method == 'POST' and request.is_ajax():
        # we did not define a form so how do we clean it?
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
