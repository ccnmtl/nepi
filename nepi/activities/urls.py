from django.conf.urls import url, patterns
'''Want to switch to class based views but not sure how'''
from nepi.activities.views import (
    UpdateConversationView, CreateConversationView, SaveResponse,
    LastResponse, SaveRetentionResponse, SaveCalendarResponse)


urlpatterns = patterns(
    '',
    url(r'^class_create_conversation/(?P<pk>\d+)/$',
        CreateConversationView.as_view(),
        name='create_conversation'),
    url(r'^update_conversation/(?P<pk>\d+)/$',
        UpdateConversationView.as_view(),
        name='update_conversation'),
    url(r'^get_click/$',
        SaveResponse.as_view(),
        name='save-response'),
    url(r'^get_last/$',
        LastResponse.as_view()),
    url(r'^retention_click/$',
        SaveRetentionResponse.as_view(),
        name='retention_click'),
    url(r'^calendar_click/$',
        SaveCalendarResponse.as_view(),
        name='calendar_click'),
)
