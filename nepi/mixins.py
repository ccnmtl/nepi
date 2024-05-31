import json

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http.response import HttpResponse, HttpResponseForbidden, \
    HttpResponseNotAllowed
from django.utils.decorators import method_decorator

from nepi.main.models import LearningModule


def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


class JSONResponseMixin(object):
    def dispatch(self, *args, **kwargs):
        if not is_ajax(self.request):
            return HttpResponseNotAllowed("")

        return super(JSONResponseMixin, self).dispatch(*args, **kwargs)

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return HttpResponse(json.dumps(context),
                            content_type='application/json',
                            **response_kwargs)


class LoggedInMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(*args, **kwargs)


class AdministrationOnlyMixin(object):
    def dispatch(self, *args, **kwargs):
        if self.request.user.profile.is_student():
            return HttpResponseForbidden("forbidden")
        return super(AdministrationOnlyMixin, self).dispatch(*args, **kwargs)


class IcapAdministrationOnlyMixin(object):
    def dispatch(self, *args, **kwargs):
        if not self.request.user.profile.is_icap():
            return HttpResponseForbidden("forbidden")
        return super(IcapAdministrationOnlyMixin, self).dispatch(*args,
                                                                 **kwargs)


class LoggedInMixinStaff(object):
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixinStaff, self).dispatch(*args, **kwargs)


class LoggedInMixinSuperuser(object):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixinSuperuser, self).dispatch(*args, **kwargs)


class InitializeHierarchyMixin(object):
    def dispatch(self, *args, **kwargs):
        module = kwargs.pop('module', 'optionb')
        language = kwargs.pop('language')

        hierarchy = LearningModule.get_hierarchy_for_language(module, language)

        self.hierarchy_name = hierarchy.name
        self.hierarchy_base = hierarchy.base_url

        return super(InitializeHierarchyMixin, self).dispatch(*args, **kwargs)
