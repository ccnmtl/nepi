import os.path

import debug_toolbar
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import (
    password_change, password_change_done, password_reset_done,
    password_reset_confirm, password_reset_complete)
from django.views.generic import TemplateView

from nepi.main.views import (
    CreateGroupView, UpdateGroupView, DeleteGroupView, CreateSchoolView,
    UpdateSchoolView, ContactView, RegistrationView, JoinGroup, HomeView,
    GroupDetail, LeaveGroup, SchoolChoiceView, SchoolGroupChoiceView,
    ArchiveGroupView, ConfirmFacultyView, DenyFacultyView, UserProfileView,
    RemoveStudent, ReportView, DownloadableReportView, StudentGroupDetail,
    PeopleView, PeopleFilterView, RosterDetail, ConfirmLanguageView,
    NepiPageView, NepiEditView)


admin.autodiscover()


site_media_root = os.path.join(os.path.dirname(__file__), "../media")

redirect_after_logout = getattr(settings, 'LOGOUT_REDIRECT_URL', None)
auth_urls = (r'^accounts/', include('django.contrib.auth.urls'))
logout_page = (r'^accounts/logout/$', 'django.contrib.auth.views.logout',
               {'next_page': redirect_after_logout})
admin_logout_page = (r'^accounts/logout/$',
                     'django.contrib.auth.views.logout',
                     {'next_page': '/admin/'})

if hasattr(settings, 'CAS_BASE'):
    auth_urls = (r'^accounts/', include('djangowind.urls'))
    logout_page = (r'^accounts/logout/$', 'djangowind.views.logout',
                   {'next_page': '/'})
    admin_logout_page = (r'^admin/logout/$',
                         'djangowind.views.logout',
                         {'next_page': redirect_after_logout})

urlpatterns = patterns(
    '',
    (r'^account_created/',
     TemplateView.as_view(template_name="flatpages/account_created.html")),
    (r'^email_sent/',
     TemplateView.as_view(template_name="flatpages/contact_email_sent.html")),

    url(r'^accounts/reset/(?P<uidb36>[0-9A-Za-z]{1,13})'
        '-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        name='password_reset_confirm'),
    admin_logout_page,
    logout_page,
    auth_urls,
    url(r'^$', HomeView.as_view(), name="home"),
    (r'^admin/', include(admin.site.urls)),

    url(r'^i18n/', include('django.conf.urls.i18n')),

    url(r'^contact/$', ContactView.as_view(), name='contactus'),
    url(r'^register/$', RegistrationView.as_view(), name='register'),

    # password change & reset. overriding to gate them.
    url(r'^accounts/password_change/$', password_change,
        name='password_change'),
    url(r'^accounts/password_change/done/$',
        password_change_done,
        name='password_change_done'),
    url(r'^password/reset/done/$', password_reset_done,
        name='password_reset_done'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        password_reset_confirm,
        name='password_reset_confirm'),
    url(r'^password/reset/complete/$',
        password_reset_complete, name='password_reset_complete'),

    # confirm language choice
    url(r'^confirm-language/$',
        ConfirmLanguageView.as_view(), name='confirm-language-choice'),

    # json object delivery
    url(r'^schools/(?P<country_id>\w[^/]*)/$',
        SchoolChoiceView.as_view(), name='school-choice'),
    url(r'^groups/(?P<school_id>\d+)/$', SchoolGroupChoiceView.as_view()),

    # dashboard base views
    url(r'^dashboard/reports/$', ReportView.as_view(),
        name='report-view'),
    url(r'^dashboard/reports/download/$', DownloadableReportView.as_view(),
        name='report-download'),
    (r'^dashboard/people/$', PeopleView.as_view()),
    (r'^dashboard/people/filter/', PeopleFilterView.as_view()),
    url(r'^dashboard/$', UserProfileView.as_view(), name='dashboard'),

    # groups
    url(r'^join_group/$', JoinGroup.as_view(), name='join-group'),
    url(r'^leave_group/$', LeaveGroup.as_view(), name='leave-group'),
    url(r'^create_group/$', CreateGroupView.as_view(),
        name='create-group'),
    (r'^edit_group/$', UpdateGroupView.as_view()),
    url(r'^delete_group/$', DeleteGroupView.as_view()),
    url(r'^archive_group/$', ArchiveGroupView.as_view()),
    url(r'^group_details/(?P<pk>\d+)/$',
        GroupDetail.as_view(), name='group-details'),
    url(r'^roster_details/(?P<pk>\d+)/$',
        RosterDetail.as_view(), name='roster-details'),
    url(r'^student_details/(?P<group_id>\d+)/(?P<student_id>\d+)/$',
        StudentGroupDetail.as_view(), name='student-group-details'),
    url(r'^remove_student/$', RemoveStudent.as_view(), name="remove-student"),

    # ICAP related pages
    (r'^faculty/confirm/$', ConfirmFacultyView.as_view()),
    (r'^faculty/deny/$', DenyFacultyView.as_view()),
    (r'^add_school/$', CreateSchoolView.as_view()),
    (r'^edit_school/(?P<pk>\d+)/$', UpdateSchoolView.as_view()),

    url(r'^captcha/', include('captcha.urls')),
    (r'^activities/', include('nepi.activities.urls')),

    url(r'^_impersonate/', include('impersonate.urls')),
    (r'^stats/$', TemplateView.as_view(template_name="stats.html")),
    (r'smoketest/', include('smoketest.urls')),
    (r'^site_media/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': site_media_root}),
    (r'^uploads/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

    (r'^quizblock/', include('quizblock.urls')),
    (r'^pagetree/', include('pagetree.urls')),

    (r'^pages/(?P<module>\w[^/]*)/(?P<language>\w[^/]*)/edit/(?P<path>.*)$',
     NepiEditView.as_view(),
     {}, 'edit-page'),
    (r'^pages/(?P<module>\w[^/]*)/(?P<language>\w[^/]*)/(?P<path>.*)$',
     NepiPageView.as_view()),
)


if settings.DEBUG:
    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)))
