from django.conf.urls.defaults import patterns, url
urlpatterns = patterns(
    '',
    url(r'^export_csv/(?P<section_id>\d+)/$',
        'wacep.analytics.views.export_csv',
        name="export_csv"),

    url(r'^course_table/(?P<section_id>\d+)/$',
        'wacep.analytics.views.course_table',
        name="course_table"),

)
