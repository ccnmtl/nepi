from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.conf import settings
import nepi.main.views
from django.views.generic import TemplateView
import os.path
admin.autodiscover()
import staticmedia
from nepi.main.views import (CreateCourseView, UpdateCourseView,
                             DeleteCourseView, StudentClassStatView,
                             GetSchoolCourses, CreateSchoolView,
                             UpdateSchoolView, ContactView,
                             RegistrationView, GetCountries,
                             StudentDashboard, JoinCourse,
                             GetCountrySchools, FacultyDashboard,
                             ICAPDashboard, Home, AddCourse,
                             UpdateProfileView, FacultyCountries,
                             FacultyCountrySchools, ThankYou)


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
    (r'^thank_you_reg/',
     TemplateView.as_view(template_name="flatpages/registration_thanks.html")),
    (r'^thank_you_school/',
     TemplateView.as_view(template_name="flatpages/school_added.html")),
)


urlpatterns += patterns(
    '',
    auth_urls,
    logout_page,
    url(r'^$', Home.as_view(), name="home"),
    (r'^admin/', include(admin.site.urls)),

    # flat and universally accessible pages
    (r'^contact/$', ContactView.as_view()),
    (r'^thanks_course/(?P<crs_id>\d+)/$', 'nepi.main.views.thanks_course'),
    
#     '''ThankYou View --> want to indicate what we are thanking user for,
#     and have one single modal/alert thanking them for whatever it is they
#     have done, may later extend to take argument to direct them back to
#     the tab they were on/active
#     Situations:
#     1. Registering for site
#     2. Joining Group
#     3. Creating Group
#     '''
    #(r'^thank_you/$', ThankYou.as_view(), name="thank-you-reg"),
    # (r'^thanks_you_j/(?P<grp_id>\d+)/$', ThankYou.as_view(), name="thank-you-join"),
    # (r'^thanks_you_c/(?P<grp_id>\d+)/$', ThankYou.as_view(), name="thank-you-create"),
    
    # profile related views
    url(r'^register/$', RegistrationView.as_view(), name='register'),
    url(r'^update_profile/(?P<pk>\d+)/$', UpdateProfileView.as_view(),
        name='update-profile'),

    # dashboard base views
    url(r'^student-dashboard/$',
        StudentDashboard.as_view(), name='student-dashboard'),
    url(r'^faculty-dashboard/$',
        FacultyDashboard.as_view(), name='faculty-dashboard'),
    url(r'^icap-dashboard/$',
        ICAPDashboard.as_view(), name='icap-dashboard'),

    # functionality to join a course
    url(r'^join_course/$', JoinCourse.as_view(), name='join-course'),
    url(r'^get_countries/$', GetCountries.as_view()),
    url(r'^get_schools/$', GetCountrySchools.as_view()),
    url(r'^get_schools/(?P<pk>\d+)/$',
        GetCountrySchools.as_view(), name='get-country-schools'),
    url(r'^get_courses/$', GetSchoolCourses.as_view()),

    # need custom yet almost identical templates for requesting faculty access
    url(r'^faculty_countries/$', FacultyCountries.as_view()),
    url(r'^faculty_schools/$', FacultyCountrySchools.as_view()),

    # functionality for teacher create a course
    url(r'^add_course/$',
        AddCourse.as_view(), name='add-course'),
    (r'^create_course/$', CreateCourseView.as_view()),
    (r'^edit_course/(?P<pk>\d+)/$', UpdateCourseView.as_view()),
    url(r'^delete_course/(?P<pk>\d+)/$', DeleteCourseView.as_view(),
        name='delete-course'),
    (r'^course_students/$', 'nepi.main.views.course_students'),
    (r'^remove_student/$', 'nepi.main.views.remove_student'),
    #(r'^course_results/$', 'nepi.main.views.course_results'),

    # ICAP related pages
    (r'^add_school/$', CreateSchoolView.as_view()),
    url(r'^view_course_stats/(?P<pk>\d+)/', StudentClassStatView.as_view(),
        name='view-course-stats'),
    (r'^edit_school/(?P<pk>\d+)/$', UpdateSchoolView.as_view()),
    # Teacher related pages
    #(r'^view_students/$', 'nepi.main.views.view_students'),
    #'nepi.main.views.create_course'),

    (r'^accessible/(?P<section_slug>.*)/$',
     'is_accessible', {}, 'is-accessible'),

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
