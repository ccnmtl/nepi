from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
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
    auth_urls,
    logout_page,
    (r'^$', 'nepi.main.views.index'),
    (r'^en/', 'nepi.main.views.home_en'),
    (r'^fr/', 'nepi.main.views.home_fr'),
    (r'^pr/', 'nepi.main.views.home_pr'),
    (r'^modules/en/', 'nepi.main.views.moduls_en'),
    (r'^modules/fr/', 'nepi.main.views.modules_fr'),
    (r'^modules/pr/', 'nepi.main.views.modules_pr'),
    (r'^module/(?P<mod_id>\d+)/en/', 'nepi.main.views.index'),
    (r'^module/(?P<mod_id>\d+)/fr/', 'nepi.main.views.index'),
    (r'^module/(?P<mod_id>\d+)/pr/', 'nepi.main.views.index'),
    (r'^admin/', include(admin.site.urls)),
    url(r'^_impersonate/', include('impersonate.urls')),
    (r'^stats/$', TemplateView.as_view(template_name="stats.html")),
    (r'smoketest/', include('smoketest.urls')),
    (r'^site_media/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': site_media_root}),
    (r'^uploads/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
) + staticmedia.serve()
