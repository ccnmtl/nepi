import os.path

import debug_toolbar
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import (
    PasswordChangeView, PasswordChangeDoneView,
    PasswordResetConfirmView, PasswordResetView, PasswordResetDoneView)
import django.contrib.auth.views
from django.urls import include, path, re_path
from django.views.generic import TemplateView
import django.views.static
from django_cas_ng import views as cas_views
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

urlpatterns = [
    path('account_created/',
         TemplateView.as_view(template_name="flatpages/account_created.html")),
    path('email_sent/', TemplateView.as_view(
        template_name="flatpages/contact_email_sent.html")),

    path('accounts/', include('django.contrib.auth.urls')),
    path('cas/login', cas_views.LoginView.as_view(),
         name='cas_ng_login'),
    path('cas/logout', cas_views.LogoutView.as_view(),
         name='cas_ng_logout'),

    path('', HomeView.as_view(), name="home"),
    path('admin/', admin.site.urls),

    path('i18n/', include('django.conf.urls.i18n')),

    path('about/', TemplateView.as_view(
        template_name='main/about.html'), name='about'),
    path('help/', TemplateView.as_view(
        template_name='main/help.html'), name='help'),
    path('contact/', ContactView.as_view(), name='contactus'),

    path('register/', RegistrationView.as_view(), name='register'),
    # password change & reset. overriding to gate them.
    path('accounts/password_change/', PasswordChangeView.as_view(),
         name='password_change'),
    path('accounts/password_change/done/',
         PasswordChangeDoneView.as_view(),
         name='password_change_done'),
    path('password/reset/done/', PasswordResetView.as_view(),
         name='password_reset_done'),
    re_path(
        r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'),
    path('password/reset/complete/',
         PasswordResetDoneView.as_view(), name='password_reset_complete'),

    # confirm language choice
    path('confirm-language/',
         ConfirmLanguageView.as_view(), name='confirm-language-choice'),

    # json object delivery
    re_path(r'^schools/(?P<country_id>\w[^/]*)/$',
            SchoolChoiceView.as_view(), name='school-choice'),
    re_path(r'^groups/(?P<school_id>\d+)/$', SchoolGroupChoiceView.as_view()),

    # dashboard base views
    path('dashboard/reports/', ReportView.as_view(),
         name='report-view'),
    path('dashboard/reports/download/', DownloadableReportView.as_view(),
         name='report-download'),
    path('dashboard/people/', PeopleView.as_view()),
    path('dashboard/people/filter/', PeopleFilterView.as_view()),
    path('dashboard/', UserProfileView.as_view(), name='dashboard'),

    # groups
    path('join_group/', JoinGroup.as_view(), name='join-group'),
    path('leave_group/', LeaveGroup.as_view(), name='leave-group'),
    path('create_group/', CreateGroupView.as_view(), name='create-group'),
    path('edit_group/', UpdateGroupView.as_view()),
    path('delete_group/', DeleteGroupView.as_view()),
    path('archive_group/', ArchiveGroupView.as_view()),
    re_path(r'^group_details/(?P<pk>\d+)/$', GroupDetail.as_view(),
            name='group-details'),
    path('add_to_group/', AddUserToGroup.as_view(), name='add-to-group'),
    re_path(r'^roster_details/(?P<pk>\d+)/$', RosterDetail.as_view(),
            name='roster-details'),
    re_path(r'^student_details/(?P<group_id>\d+)/(?P<student_id>\d+)/$',
            StudentGroupDetail.as_view(), name='student-group-details'),
    path('remove_student/', RemoveStudent.as_view(), name="remove-student"),

    # ICAP related pages
    path('faculty/confirm/', ConfirmFacultyView.as_view()),
    path('faculty/deny/', DenyFacultyView.as_view()),
    path('add_school/', CreateSchoolView.as_view()),
    re_path(r'^edit_school/(?P<pk>\d+)/$', UpdateSchoolView.as_view()),

    path('captcha/', include('captcha.urls')),
    path('activities/', include('nepi.activities.urls')),

    path('_impersonate/', include('impersonate.urls')),
    path('stats/', TemplateView.as_view(template_name="stats.html")),
    path('smoketest/', include('smoketest.urls')),
    re_path(r'^site_media/(?P<path>.*)$',
            django.views.static.serve, {'document_root': site_media_root}),
    re_path(r'^uploads/(?P<path>.*)$',
            django.views.static.serve, {'document_root': settings.MEDIA_ROOT}),

    path('quizblock/', include('quizblock.urls')),
    path('pagetree/', include('pagetree.urls')),

    re_path(r'^pages/main/(?P<path>.*)$', NepiDeprecatedPageView.as_view()),

    re_path(
        r'^pages/(?P<module>\w[^/]*)/(?P<language>\w[^/]*)/edit/(?P<path>.*)$',
        NepiEditView.as_view(),
        {}, 'edit-page'),
    re_path(
        r'^pages/(?P<module>\w[^/]*)/(?P<language>\w[^/]*)/(?P<path>.*)$',
        NepiPageView.as_view()),
]


if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls))
    ]
