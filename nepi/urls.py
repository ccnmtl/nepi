import os.path

import debug_toolbar
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import (
    PasswordChangeView, PasswordChangeDoneView,
    PasswordResetConfirmView, PasswordResetView, PasswordResetDoneView)
import django.contrib.auth.views
from django.views.generic import TemplateView
import django.views.static

from nepi.main.views import (
    CreateGroupView, UpdateGroupView, DeleteGroupView, CreateSchoolView,
    UpdateSchoolView, ContactView, RegistrationView, JoinGroup, HomeView,
    GroupDetail, LeaveGroup, SchoolChoiceView, SchoolGroupChoiceView,
    ArchiveGroupView, ConfirmFacultyView, DenyFacultyView, UserProfileView,
    RemoveStudent, ReportView, DownloadableReportView, StudentGroupDetail,
    PeopleView, PeopleFilterView, RosterDetail, ConfirmLanguageView,
    NepiPageView, NepiEditView, NepiDeprecatedPageView,
    AddUserToGroup)


admin.autodiscover()


site_media_root = os.path.join(os.path.dirname(__file__), "../media")

auth_urls = url(r'^accounts/', include('django.contrib.auth.urls'))
if hasattr(settings, 'CAS_BASE'):
    auth_urls = url(r'^accounts/', include('djangowind.urls'))


urlpatterns = [
    url(r'^account_created/',
        TemplateView.as_view(template_name="flatpages/account_created.html")),
    url(r'^email_sent/', TemplateView.as_view(
        template_name="flatpages/contact_email_sent.html")),

    auth_urls,
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^admin/', admin.site.urls),

    url(r'^i18n/', include('django.conf.urls.i18n')),

    url(r'^about/$', TemplateView.as_view(
        template_name='main/about.html'), name='about'),
    url(r'^help/$', TemplateView.as_view(
        template_name='main/help.html'), name='help'),
    url(r'^contact/$', ContactView.as_view(), name='contactus'),

    url(r'^register/$', RegistrationView.as_view(), name='register'),
    # password change & reset. overriding to gate them.
    url(r'^accounts/password_change/$', PasswordChangeView.as_view(),
        name='password_change'),
    url(r'^accounts/password_change/done/$',
        PasswordChangeDoneView.as_view(),
        name='password_change_done'),
    url(r'^password/reset/done/$', PasswordResetView.as_view(),
        name='password_reset_done'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'),
    url(r'^password/reset/complete/$',
        PasswordResetDoneView.as_view(), name='password_reset_complete'),

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
    url(r'^dashboard/people/$', PeopleView.as_view()),
    url(r'^dashboard/people/filter/', PeopleFilterView.as_view()),
    url(r'^dashboard/$', UserProfileView.as_view(), name='dashboard'),

    # groups
    url(r'^join_group/$', JoinGroup.as_view(), name='join-group'),
    url(r'^leave_group/$', LeaveGroup.as_view(), name='leave-group'),
    url(r'^create_group/$', CreateGroupView.as_view(), name='create-group'),
    url(r'^edit_group/$', UpdateGroupView.as_view()),
    url(r'^delete_group/$', DeleteGroupView.as_view()),
    url(r'^archive_group/$', ArchiveGroupView.as_view()),
    url(r'^group_details/(?P<pk>\d+)/$', GroupDetail.as_view(),
        name='group-details'),
    url(r'^add_to_group/$', AddUserToGroup.as_view(), name='add-to-group'),
    url(r'^roster_details/(?P<pk>\d+)/$', RosterDetail.as_view(),
        name='roster-details'),
    url(r'^student_details/(?P<group_id>\d+)/(?P<student_id>\d+)/$',
        StudentGroupDetail.as_view(), name='student-group-details'),
    url(r'^remove_student/$', RemoveStudent.as_view(), name="remove-student"),

    # ICAP related pages
    url(r'^faculty/confirm/$', ConfirmFacultyView.as_view()),
    url(r'^faculty/deny/$', DenyFacultyView.as_view()),
    url(r'^add_school/$', CreateSchoolView.as_view()),
    url(r'^edit_school/(?P<pk>\d+)/$', UpdateSchoolView.as_view()),

    url(r'^captcha/', include('captcha.urls')),
    url(r'^activities/', include('nepi.activities.urls')),

    url(r'^_impersonate/', include('impersonate.urls')),
    url(r'^stats/$', TemplateView.as_view(template_name="stats.html")),
    url(r'smoketest/', include('smoketest.urls')),
    url(r'^site_media/(?P<path>.*)$',
        django.views.static.serve, {'document_root': site_media_root}),
    url(r'^uploads/(?P<path>.*)$',
        django.views.static.serve, {'document_root': settings.MEDIA_ROOT}),

    url(r'^quizblock/', include('quizblock.urls')),
    url(r'^pagetree/', include('pagetree.urls')),

    url(r'^pages/main/(?P<path>.*)$', NepiDeprecatedPageView.as_view()),

    url(r'^pages/(?P<module>\w[^/]*)/(?P<language>\w[^/]*)/edit/(?P<path>.*)$',
        NepiEditView.as_view(),
        {}, 'edit-page'),
    url(r'^pages/(?P<module>\w[^/]*)/(?P<language>\w[^/]*)/(?P<path>.*)$',
        NepiPageView.as_view()),
]


if settings.DEBUG:
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls))
    ]
