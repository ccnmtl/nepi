from django.conf.urls.defaults import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.conf import settings
from nepi.main.views import CreateAccountForm
#from registration.backends.default.views import RegistrationView
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
    (r'^captcha/$', include('captcha.urls')),
    (r'^$', 'nepi.main.views.index'),
    (r'^admin/', include(admin.site.urls)),
    (r'^home/$', 'nepi.main.views.home'),
    (r'^register/$', 'nepi.main.views.register'),
    (r'^thank_you/$', 'nepi.main.views.thank_you'),
    (r'^login/$', 'nepi.main.views.nepi_login'),
    (r'^logout/$', 'nepi.main.views.logout'),
    (r'^add_school/$', 'nepi.main.views.add_school'),
    (r'^contact/$', 'nepi.main.views.contact'),
    #(r'^show_teachers/$', 'nepi.main.views.add_teachers'),
    #(r'^registration_complete/$', 'nepi.main.views.registration_complete'),
    (r'^about/$', 'nepi.main.views.about'),
    (r'^help_page/$', 'nepi.main.views.help_page'),
    (r'^contact/$', 'nepi.main.views.contact'),
    url(r'^_impersonate/', include('impersonate.urls')),
    (r'^munin/', include('munin.urls')),
    (r'^stats/$', TemplateView.as_view(template_name="stats.html")),
    (r'smoketest/', include('smoketest.urls')),
    (r'^site_media/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': site_media_root}),
    (r'^uploads/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
) + staticmedia.serve()


# urlpatterns += i18n_patterns(
#     '',
#     url(_(r'^home/'), 'nepi.main.views.test_view', name='home'),
#     url(_(r'^modules/'), 'nepi.main.views.moduls_en', name='modules'),
#     url(_(r'^lesson/(?P<mod_id>\d+)/'), 'nepi.main.views.index', name='lesson'),
# )
