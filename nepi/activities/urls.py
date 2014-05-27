from django.conf.urls import url, patterns
'''Want to switch to class based views but not sure how'''
from nepi.activities.views import UpdateConversationView
from nepi.activities.views import DeleteConversationView
from nepi.activities.views import ScenarioListView
from nepi.activities.views import ScenarioDetailView
from nepi.activities.views import ScenarioDeleteView
# from nepi.activities.views import CreateConverstionView


urlpatterns = patterns(
    '',
    #url(r'^class_create_conversation/(?P<pk>\d+)/$',
    #    CreateConverstionView.as_view(),
    #    name='class_create_conversation'),
    url(r'^create_conversation/(?P<pk>\d+)/$',
        'nepi.activities.views.add_conversation',
        name='create_conversation'),
    url(r'^update_conversation/(?P<pk>\d+)/$',
        UpdateConversationView.as_view()),
    url(r'^delete_conversation/(?P<pk>\d+)/$',
        DeleteConversationView.as_view()),
    url(r'^classview_scenariolist/$',
        ScenarioListView.as_view()),
    url(r'^delete_scenario/(?P<pk>\d+)/$',
        ScenarioDeleteView.as_view()),
    url(r'^scenario_display/(?P<pk>\d+)/$',
        ScenarioDetailView.as_view()),
    (r'^get_click/$', 'nepi.activities.views.get_click'),
    url(r'^get_last/$', 'nepi.activities.views.get_last'),
)
