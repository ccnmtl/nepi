from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
#from pagetree.generic.views import PageView, EditView, InstructorView
import os.path
admin.autodiscover()
import staticmedia

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
        {'next_page': redirect_after_logout})

urlpatterns = patterns(
    '',
    (r'^about/',
     TemplateView.as_view(template_name="flatpages/about.html")),
    (r'^help/',
     TemplateView.as_view(template_name="flatpages/help.html")),
    #(r'^contact/',
    # TemplateView.as_view(template_name="flatpages/contact.html")),
    (r'^thank_you_reg/', TemplateView.as_view(template_name="flatpages/registration_thanks.html")), #template is thanks html
    (r'^thank_you_school/', TemplateView.as_view(template_name="flatpages/school_added.html")), # template is school_added
)

urlpatterns += patterns(
    '',
    auth_urls,
    logout_page,
    url(r'^$', 'nepi.main.views.index', name="index"),
    (r'^admin/', include(admin.site.urls)),

    #login/logout
    (r'^login/$', 'nepi.main.views.nepi_login'),
    (r'^logout/$', 'nepi.main.views.logout_view'),

    # flat and universally accessible pages
    (r'^home/$', 'nepi.main.views.home'),
    (r'^contact/$', 'nepi.main.views.contact'),
    (r'^register/$', 'nepi.main.views.register'),
    #(r'^select_language/$', 'nepi.main.views.select_language'),

    # ICAP related pages
    #(r'^pending_teachers/$', 'nepi.main.views.pending_teachers'),
    (r'^view_schools/$', 'nepi.main.views.view_schools'),
    (r'^view_region/$', 'nepi.main.views.view_region'),
    (r'^add_school/$', 'nepi.main.views.add_school'),
    (r'^confirm_teacher/$', 'nepi.main.views.confirm_teacher'),
    (r'^confirm_teacher/(?P<prof_id>\d+)/(?P<schl_id>\d+)/$',
     'nepi.main.views.confirm_teacher'),
    (r'^deny_teacher/(?P<prof_id>\d+)/(?P<schl_id>\d+)/$',
     'nepi.main.views.deny_teacher'),
    (r'^icapp_view_students/$', 'nepi.main.views.icapp_view_students'),

    # Teacher related pages
    #(r'^view_students/$', 'nepi.main.views.view_students'),
    (r'^create_course/$', 'nepi.main.views.create_course'),
    (r'^course_created/$', 'nepi.main.views.course_created'),
    (r'^edit_course//(?P<crs_id>\d+)/$', 'nepi.main.views.edit_course'),
    (r'^course_students/$', 'nepi.main.views.course_students'),
    #(r'^courses/$', 'nepi.main.views.courses'),
    #(r'^current_courses/$', 'nepi.main.views.current_courses'),
    (r'^remove_student/$', 'nepi.main.views.remove_student'),
    (r'^course_results/$', 'nepi.main.views.course_results'),



    # Student related pages
    (r'^thanks_course/(?P<crs_id>\d+)/$', 'nepi.main.views.thanks_course'),
    (r'^view_courses/(?P<schl_id>\d+)/$', 'nepi.main.views.view_courses'),
    (r'^join_course/$', 'nepi.main.views.join_course'),
    (r'^view_courses/(?P<schl_id>\d+)/$', 'nepi.main.views.view_courses'),



    #(r'^show_teachers/$', 'nepi.main.views.add_teachers'),
    #(r'^registration_complete/$', 'nepi.main.views.registration_complete'),

    url(r'^_impersonate/', include('impersonate.urls')),
    (r'^munin/', include('munin.urls')),
    (r'^stats/$', TemplateView.as_view(template_name="stats.html")),
    (r'smoketest/', include('smoketest.urls')),
    (r'^site_media/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': site_media_root}),
    (r'^uploads/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

    # from tobacco
    (r'^pagetree/', include('pagetree.urls')),

    # resources path -- content that's open by default
    (r'^edit/resources/(?P<path>.*)$',
     'nepi.main.views.edit_resources'),
    (r'^resources/(?P<path>.*)$',
     'nepi.main.views.resources'),

    # very important that this stays last and in this order
    (r'^pages/edit/(?P<hierarchy>\w+)/(?P<path>.*)$',
     'nepi.main.views.edit_page'),
    (r'^pages/(?P<hierarchy>\w+)/(?P<path>.*)$',
     'nepi.main.views.page'),



) + staticmedia.serve()

urlpatterns += staticfiles_urlpatterns()
