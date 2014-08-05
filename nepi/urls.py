from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
from nepi.main.views import CreateGroupView, UpdateGroupView, \
    DeleteGroupView, StudentClassStatView, CreateSchoolView, \
    UpdateSchoolView, ContactView, RegistrationView, StudentDashboard, \
    JoinGroup, FacultyDashboard, ICAPDashboard, HomeView, \
    GroupDetail, RemoveStudent, LeaveGroup, SchoolChoiceView, \
    CountryAdminDashboard, SchoolGroupChoiceView, ArchiveGroupView, \
    ConfirmFacultyView, DenyFacultyView
import nepi.main.views
import os.path
import staticmedia
admin.autodiscover()


site_media_root = os.path.join(os.path.dirname(__file__), "../media")

redirect_after_logout = getattr(settings, 'LOGOUT_REDIRECT_URL', None)
auth_urls = (r'^accounts/', include('django.contrib.auth.urls'))
logout_page = (
    r'^accounts/logout/$',
    'django.contrib.auth.views.logout',
    {'next_page': redirect_after_logout})
if hasattr(settings, 'WIND_BASE'):
    auth_urls = (r'^accounts/', include('djangowind.urls'))
    logout_page = (
        r'^accounts/logout/$',
        'djangowind.views.logout',
        {'next_page': '/'})

urlpatterns = patterns(
    '',
    (r'^about/',
     TemplateView.as_view(template_name="flatpages/about.html")),
    (r'^help/',
     TemplateView.as_view(template_name="flatpages/help.html")),
    (r'^account_created/',
     TemplateView.as_view(template_name="flatpages/account_created.html")),
    (r'^email_sent/',
     TemplateView.as_view(template_name="flatpages/contact_email_sent.html")),

    auth_urls,
    logout_page,
    url(r'^$', HomeView.as_view(), name="home"),
    (r'^admin/', include(admin.site.urls)),

    (r'^contact/$', ContactView.as_view()),
    url(r'^register/$', RegistrationView.as_view(), name='register'),

    # json object delivery
    url(r'^schools/(?P<country_id>\w[^/]*)/$',
        SchoolChoiceView.as_view(), name='school-choice'),
    url(r'^groups/(?P<school_id>\d+)/$', SchoolGroupChoiceView.as_view()),

    # dashboard base views
    url(r'^student-dashboard/(?P<pk>\d+)/$',
        StudentDashboard.as_view(), name='student-dashboard'),
    url(r'^faculty-dashboard/(?P<pk>\d+)/$',
        FacultyDashboard.as_view(), name='faculty-dashboard'),
    url(r'^country-dashboard/(?P<pk>\d+)/$',
        CountryAdminDashboard.as_view(), name='country-dashboard'),
    url(r'^icap-dashboard/(?P<pk>\d+)/$',
        ICAPDashboard.as_view(), name='icap-dashboard'),

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
    (r'^remove_student/$', RemoveStudent.as_view()),

    # ICAP related pages
    (r'^faculty/confirm/$', ConfirmFacultyView.as_view()),
    (r'^faculty/deny/$', DenyFacultyView.as_view()),
    (r'^add_school/$', CreateSchoolView.as_view()),
    url(r'^view_group/(?P<pk>\d+)/', StudentClassStatView.as_view(),
        name='view-group'),
    (r'^edit_school/(?P<pk>\d+)/$', UpdateSchoolView.as_view()),
    # Teacher related pages
    #(r'^view_students/$', 'nepi.main.views.view_students'),
    #'nepi.main.views.create_group'),

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

    (r'^pages/main/edit/(?P<path>.*)$',
     nepi.main.views.EditPage.as_view(),
     {}, 'edit-page'),

    (r'^pages/activities/edit/(?P<path>.*)$',
     nepi.main.views.EditPage.as_view(),
     {}, 'edit-page'),

    (r'^pages/main/(?P<path>.*)$', nepi.main.views.ViewPage.as_view()),


) + staticmedia.serve()

urlpatterns += staticfiles_urlpatterns()
