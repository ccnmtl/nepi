# flake8: noqa
from settings_shared import *

TEMPLATE_DIRS = (
    "/var/www/nepi/nepi/nepi/templates",
)

MEDIA_ROOT = '/var/www/nepi/uploads/'
# put any static media here to override app served static media
STATICMEDIA_MOUNTS = (
    ('/sitemedia', '/var/www/nepi/nepi/sitemedia'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'nepi',
        'HOST': '',
        'PORT': 6432,
        'USER': '',
        'PASSWORD': '',
    }
}

COMPRESS_ROOT = "/var/www/nepi/nepi/media/"
DEBUG = False
TEMPLATE_DEBUG = DEBUG
STAGING_ENV = True

STATSD_PREFIX = 'nepi-staging'

if 'migrate' not in sys.argv:
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')

LOCALE_PATHS = ('/var/www/nepi/nepi/locale',)

try:
    from local_settings import *
except ImportError:
    pass
