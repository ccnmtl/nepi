from django.conf.urls import patterns
from activities.views import CreateNurseConversationView
from activities.views import UpdateNurseConversationView
from activities.views import CreatePatientConversationView
from activities.views import UpdatePatientConversationView
from activities.views import CreateConversationDialogView
from activities.views import CreateConversationScenarioView
from activities.views import UpdateConversationScenarioView
from activities.views import CreateConversationView
from activities.views import UpdateConversationView
from pagetree.generic.views import PageView

urlpatterns = patterns(
    #'activities.views',
    # Interactive Links
    #(r'^conversation/(?P<id>\d+)/$', 'Conversation.as_view()'),
    (r'^create_conversation/$', 'CreateConversationView.as_view()'),
#    (r'^update_conversation/$', 'UpdateConversationView.as_view()'),
#    (r'^edit_lab/(?P<id>\d+)/$', 'edit_lab', {}, 'edit-lab'),
#    (r'^edit_lab/(?P<id>\d+)/add_test/$',
#     'add_test_to_lab', {}, 'add-test-to-lab'),
#    (r'^edit_lab/(?P<id>\d+)/add_csv/$',
#     'add_csv_to_lab', {}, 'add-csv-to-lab'),
#    (r'^edit_test/(?P<id>\d+)/$', 'edit_test', {}, 'edit-test'),
#    (r'^delete_test/(?P<id>\d+)/$', 'delete_test', {}, 'delete-test'),
#    (r'^reorder_tests/(?P<id>\d+)/$', 'reorder_tests', {}, 'reorder-tests'),
)
