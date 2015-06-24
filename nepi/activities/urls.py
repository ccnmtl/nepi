from django.conf.urls import url, patterns
from nepi.activities.views import (
    CreateConversationView, UpdateConversationView,
    SaveResponse, LastResponse, SaveRetentionResponse, SaveCalendarResponse)


urlpatterns = patterns(
    '',
    url(r'^create_conversation/(?P<pk>\d+)/(?P<type>\w)/$',
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
