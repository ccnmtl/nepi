import os.path

import debug_toolbar
from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.contrib.auth.views import (
    PasswordChangeView, PasswordChangeDoneView,
    PasswordResetConfirmView, PasswordResetView, PasswordResetDoneView)
import django.contrib.auth.views
from django.urls import path, re_path
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
    re_path(r'^account_created/',
            TemplateView.as_view(
                template_name="flatpages/account_created.html")),
    re_path(r'^email_sent/', TemplateView.as_view(
            template_name="flatpages/contact_email_sent.html")),

    re_path(r'^accounts/', include('django.contrib.auth.urls')),
    path('cas/login', cas_views.LoginView.as_view(),
         name='cas_ng_login'),
    path('cas/logout', cas_views.LogoutView.as_view(),
         name='cas_ng_logout'),

    re_path(r'^$', HomeView.as_view(), name="home"),
    re_path(r'^admin/', admin.site.urls),

    re_path(r'^i18n/', include('django.conf.urls.i18n')),

    re_path(r'^about/$', TemplateView.as_view(
            template_name='main/about.html'), name='about'),
    re_path(r'^help/$', TemplateView.as_view(
            template_name='main/help.html'), name='help'),
    re_path(r'^contact/$', ContactView.as_view(), name='contactus'),

    re_path(r'^register/$', RegistrationView.as_view(), name='register'),
    # password change & reset. overriding to gate them.
    re_path(r'^accounts/password_change/$', PasswordChangeView.as_view(),
            name='password_change'),
    re_path(r'^accounts/password_change/done/$',
            PasswordChangeDoneView.as_view(),
            name='password_change_done'),
    re_path(r'^password/reset/done/$', PasswordResetView.as_view(),
            name='password_reset_done'),
    re_path(
        r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'),
    re_path(r'^password/reset/complete/$',
            PasswordResetDoneView.as_view(), name='password_reset_complete'),

    # confirm language choice
    re_path(r'^confirm-language/$',
            ConfirmLanguageView.as_view(), name='confirm-language-choice'),

    # json object delivery
    re_path(r'^schools/(?P<country_id>\w[^/]*)/$',
            SchoolChoiceView.as_view(), name='school-choice'),
    re_path(r'^groups/(?P<school_id>\d+)/$', SchoolGroupChoiceView.as_view()),

    # dashboard base views
    re_path(r'^dashboard/reports/$', ReportView.as_view(),
            name='report-view'),
    re_path(r'^dashboard/reports/download/$', DownloadableReportView.as_view(),
            name='report-download'),
    re_path(r'^dashboard/people/$', PeopleView.as_view()),
    re_path(r'^dashboard/people/filter/', PeopleFilterView.as_view()),
    re_path(r'^dashboard/$', UserProfileView.as_view(), name='dashboard'),

    # groups
    re_path(r'^join_group/$', JoinGroup.as_view(), name='join-group'),
    re_path(r'^leave_group/$', LeaveGroup.as_view(), name='leave-group'),
    re_path(r'^create_group/$', CreateGroupView.as_view(),
            name='create-group'),
    re_path(r'^edit_group/$', UpdateGroupView.as_view()),
    re_path(r'^delete_group/$', DeleteGroupView.as_view()),
    re_path(r'^archive_group/$', ArchiveGroupView.as_view()),
    re_path(r'^group_details/(?P<pk>\d+)/$', GroupDetail.as_view(),
            name='group-details'),
    re_path(r'^add_to_group/$', AddUserToGroup.as_view(), name='add-to-group'),
    re_path(r'^roster_details/(?P<pk>\d+)/$', RosterDetail.as_view(),
            name='roster-details'),
    re_path(r'^student_details/(?P<group_id>\d+)/(?P<student_id>\d+)/$',
            StudentGroupDetail.as_view(), name='student-group-details'),
    re_path(r'^remove_student/$', RemoveStudent.as_view(),
            name="remove-student"),

    # ICAP related pages
    re_path(r'^faculty/confirm/$', ConfirmFacultyView.as_view()),
    re_path(r'^faculty/deny/$', DenyFacultyView.as_view()),
    re_path(r'^add_school/$', CreateSchoolView.as_view()),
    re_path(r'^edit_school/(?P<pk>\d+)/$', UpdateSchoolView.as_view()),

    re_path(r'^captcha/', include('captcha.urls')),
    re_path(r'^activities/', include('nepi.activities.urls')),

    re_path(r'^_impersonate/', include('impersonate.urls')),
    re_path(r'^stats/$', TemplateView.as_view(template_name="stats.html")),
    re_path(r'smoketest/', include('smoketest.urls')),
    re_path(r'^site_media/(?P<path>.*)$',
            django.views.static.serve, {'document_root': site_media_root}),
    re_path(r'^uploads/(?P<path>.*)$',
            django.views.static.serve, {'document_root': settings.MEDIA_ROOT}),

    re_path(r'^quizblock/', include('quizblock.urls')),
    re_path(r'^pagetree/', include('pagetree.urls')),

    re_path(r'^pages/main/(?P<path>.*)$', NepiDeprecatedPageView.as_view()),

    re_path(
        r'^pages/(?P<module>\w[^/]*)/(?P<language>\w[^/]*)/edit/(?P<path>.*)$',
        NepiEditView.as_view(),
        {}, 'edit-page'),
    re_path(r'^pages/(?P<module>\w[^/]*)/(?P<language>\w[^/]*)/(?P<path>.*)$',
            NepiPageView.as_view()),
]


if settings.DEBUG:
    urlpatterns += [
        re_path(r'^__debug__/', include(debug_toolbar.urls))
    ]
