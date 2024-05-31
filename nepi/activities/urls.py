from django.urls import re_path
from nepi.activities.views import (
    CreateConversationView, UpdateConversationView,
    SaveResponse, LastResponse, SaveRetentionResponse, SaveCalendarResponse)


urlpatterns = [
    re_path(r'^create_conversation/(?P<pk>\d+)/(?P<type>\w)/$',
            CreateConversationView.as_view(),
            name='create_conversation'),
    re_path(r'^update_conversation/(?P<pk>\d+)/$',
            UpdateConversationView.as_view(),
            name='update_conversation'),
    re_path(r'^get_click/$',
            SaveResponse.as_view(),
            name='save-response'),
    re_path(r'^get_last/$',
            LastResponse.as_view()),
    re_path(r'^retention_click/$',
            SaveRetentionResponse.as_view(),
            name='retention_click'),
    re_path(r'^calendar_click/$',
            SaveCalendarResponse.as_view(),
            name='calendar_click'),
]
