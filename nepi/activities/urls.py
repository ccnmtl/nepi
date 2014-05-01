from django.conf.urls.defaults import patterns
'''Want to switch to class based views but not sure how'''
#from nepi.activities.models import CreateConversationScenarioView
#from nepi.activities.models import UpdateConversationScenarioView
from nepi.activities.views import CreateConversationView
from nepi.activities.views import UpdateConversationView
from nepi.activities.views import DeleteConversationView
from nepi.activities.views import ConversationScenarioListView
#from pagetree.generic.views import PageView

urlpatterns = patterns(
    '',
    (r'^create_conversation/$', CreateConversationView.as_view()),
    (r'^add_conversation/(?P<pk>\d+)/$', 'nepi.activities.views.add_conversation'),
    (r'^update_conversation/(?P<pk>\d+)/$', UpdateConversationView.as_view()),
    (r'^delete_conversation/(?P<pk>\d+)/$', DeleteConversationView.as_view()),
    (r'^see_scenarios/$', ConversationScenarioListView.as_view()),
    #(r'^get_click/$', 'nepi.activities.views.add_conversation'),
    #(r'^create_scenario/$', 'CreateConversationScenarioView.as_view()'),
    #(r'^update_scenario/(?P<id>\d+)/$',
    #    'UpdateConversationScenarioView.as_view()')
)
