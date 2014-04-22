from django.conf.urls.defaults import patterns, include
'''Want to switch to class based views but not sure how'''
#from nepi.activities.models import CreateConversationScenarioView
#from nepi.activities.models import UpdateConversationScenarioView
from nepi.activities.models import CreateConversationView
from nepi.activities.models import UpdateConversationView
#from pagetree.generic.views import PageView

urlpatterns = patterns(
    '',
    (r'^create_conversation/$', CreateConversationView.as_view()),
    (r'^update_conversation/(?P<id>\d+)/$', 'UpdateConversationView.as_view()'),
#    (r'^create_scenario/$', 'CreateConversationScenarioView.as_view()'),
#    (r'^update_scenario/(?P<id>\d+)/$', 'UpdateConversationScenarioView.as_view()')
)


