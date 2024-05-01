from django.urls import path, re_path
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
    path('get_click/',
         SaveResponse.as_view(),
         name='save-response'),
    path('get_last/',
         LastResponse.as_view()),
    path('retention_click/',
         SaveRetentionResponse.as_view(),
         name='retention_click'),
    path('calendar_click/',
         SaveCalendarResponse.as_view(),
         name='calendar_click'),
]
