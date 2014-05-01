from django.conf.urls.defaults import patterns
'''Want to switch to class based views but not sure how'''
from nepi.activities.views import CreateConversationView
from nepi.activities.views import UpdateConversationView
from nepi.activities.views import DeleteConversationView
from nepi.activities.views import ConversationScenarioListView

urlpatterns = patterns(
    '',
    (r'^create_conversation/$', CreateConversationView.as_view()),
    (r'^add_conversation/(?P<pk>\d+)/$',
     'nepi.activities.views.add_conversation'),
    (r'^update_conversation/(?P<pk>\d+)/$', UpdateConversationView.as_view()),
    (r'^delete_conversation/(?P<pk>\d+)/$', DeleteConversationView.as_view()),
    (r'^see_scenarios/$', ConversationScenarioListView.as_view()),
)
