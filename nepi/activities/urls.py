from django.conf.urls import url, patterns
'''Want to switch to class based views but not sure how'''
from nepi.activities.views import (UpdateConversationView,
                                   DeleteConversationView,
                                   ScenarioListView,
                                   ScenarioDetailView,
                                   ScenarioDeleteView,
                                   CreateConverstionView,
                                   SaveResponse,
                                   LastResponse,
                                   CreateCalendar)
from nepi.activities.models import DosageActivity


urlpatterns = patterns(
    '',
    url(r'^class_create_conversation/(?P<pk>\d+)/$',
        CreateConverstionView.as_view(),
        name='create_conversation'),
    url(r'^update_conversation/(?P<pk>\d+)/$',
        UpdateConversationView.as_view(),
        name='update_conversation'),
    url(r'^delete_conversation/(?P<pk>\d+)/$',
        DeleteConversationView.as_view()),
    url(r'^classview_scenariolist/$',
        ScenarioListView.as_view()),
    url(r'^delete_scenario/(?P<pk>\d+)/$',
        ScenarioDeleteView.as_view()),
    url(r'^scenario_display/(?P<pk>\d+)/$',
        ScenarioDetailView.as_view()),
    url(r'^get_click/$',
        SaveResponse.as_view()),
    url(r'^get_last/$',
        LastResponse.as_view()),
    url(r'^create_calendar/$',
        CreateCalendar.as_view(),
        name='create_calendar'),
#     url(r'^submit/$',
#         DosageActivity.submit(),
#         name='submit')
)
