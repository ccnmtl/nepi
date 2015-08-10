# Django settings for nepi project.
import os
import sys
from django.utils.translation import ugettext_lazy as _

# in prod, something like /var/www/myapp/myapp/myapp
CURRENT_DIR = os.path.dirname(__file__)

# where the project codebase lives. eg, /var/www/myapp/myapp
PROJECT_DIR = os.path.normpath(os.path.join(CURRENT_DIR, "../"))

# where the code, uploads, etc directories live
# eg, /var/www/myapp
WEB_DIR = os.path.normpath(os.path.join(PROJECT_DIR, "../"))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()

MANAGERS = ADMINS

ACCOUNT_ACTIVATION_DAYS = 6

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'nepi',
        'HOST': '',
        'PORT': 5432,
        'USER': '',
        'PASSWORD': '',
    }
}

if 'test' in sys.argv or 'jenkins' in sys.argv:
    CAPTCHA_TEST_MODE = True

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'HOST': '',
            'PORT': '',
            'USER': '',
            'PASSWORD': '',
        }
    }

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

JENKINS_TASKS = (
    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.run_pyflakes',
)

PROJECT_APPS = [
    'nepi.main', 'nepi.activities',
]

ALLOWED_HOSTS = ['localhost',
                 '.ccnmtl.columbia.edu',
                 'elearning.icap.columbia.edu']

USE_TZ = True
TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
COMPRESS_URL = "/media/"
COMPRESS_ROOT = os.path.join(PROJECT_DIR, "media")
MEDIA_ROOT = os.path.join(WEB_DIR, "uploads")
MEDIA_URL = '/uploads/'
STATIC_URL = '/media/'
SECRET_KEY = ')ng#)ef_u@_^zvvu@dxm7ql-yb^_!a6%v3v^j3b(mp+)l+5%@h'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'djangowind.context.context_processor',
    'stagingcontext.staging_processor',
    'gacontext.ga_processor',
    'nepi.main.views.context_processor'
)

MIDDLEWARE_CLASSES = [
    'django_statsd.middleware.GraphiteRequestTimingMiddleware',
    'django_statsd.middleware.GraphiteMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'impersonate.middleware.ImpersonateMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'waffle.middleware.WaffleMiddleware',
]

ROOT_URLCONF = 'nepi.urls'

TEMPLATE_DIRS = (
    os.path.join(CURRENT_DIR, "templates"),
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django_markwhat',
    'django.contrib.staticfiles',
    'sorl.thumbnail',
    'django.contrib.admin',
    'tagging',
    'typogrify',
    'compressor',
    'django_statsd',
    'bootstrapform',
    'debug_toolbar',
    'waffle',
    'django_jenkins',
    'smoketest',
    'django_extensions',
    'impersonate',
    'nepi.main',
    'pagetree',
    'pageblocks',
    'quizblock',
    'captcha',
    'nepi.activities'
]

INTERNAL_IPS = ('127.0.0.1', )

DEBUG_TOOLBAR_PATCH_SETTINGS = False

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]

STATSD_CLIENT = 'statsd.client'
STATSD_PREFIX = 'nepi'
STATSD_HOST = '127.0.0.1'
STATSD_PORT = 8125

THUMBNAIL_SUBDIR = "thumbs"
EMAIL_SUBJECT_PREFIX = "[nepi] "
EMAIL_HOST = 'localhost'
SERVER_EMAIL = "nepi@ccnmtl.columbia.edu"
DEFAULT_FROM_EMAIL = SERVER_EMAIL


# put any static media here to override app served static media
STATICMEDIA_MOUNTS = (
    ('/sitemedia', os.path.join(PROJECT_DIR, 'sitemedia')),
)


STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)

# WIND settings

AUTHENTICATION_BACKENDS = (
    'djangowind.auth.SAMLAuthBackend',
    'django.contrib.auth.backends.ModelBackend', )
CAS_BASE = "https://cas.columbia.edu/"
WIND_PROFILE_HANDLERS = ['djangowind.auth.CDAPProfileHandler']
WIND_AFFIL_HANDLERS = ['djangowind.auth.AffilGroupMapper',
                       'djangowind.auth.StaffMapper',
                       'djangowind.auth.SuperuserMapper']
WIND_STAFF_MAPPER_GROUPS = ['tlc.cunix.local:columbia.edu']
WIND_SUPERUSER_MAPPER_GROUPS = ['anp8', 'jb2410', 'zm4', 'egr2107', 'cld2156',
                                'sld2131', 'amm8', 'mar227', 'njn2118']

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_HTTPONLY = True
LOGIN_REDIRECT_URL = "/"

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')


PAGEBLOCKS = ['pageblocks.HTMLBlockWYSIWYG',
              'pageblocks.HTMLBlock',
              'pageblocks.ImageBlock',
              'quizblock.Quiz',
              'main.AggregateQuizScore',
              'activities.ConversationScenario',
              'activities.ImageInteractive',
              'activities.CalendarChart',
              'activities.DosageActivity',
              'activities.ARTCard',
              'activities.RetentionRateCard',
              'activities.AdherenceCard']

AUTH_PROFILE_MODULE = 'nepi.main.UserProfile'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

ICAP_MAILING_LIST = 'ccnmtl-icap@ccnmtl.columbia.edu'
NEPI_MAILING_LIST = 'ccnmtl-nepi@ccnmtl.columbia.edu'

CAPTCHA_FONT_SIZE = 34

LOCALE_PATHS = (
    os.path.join(PROJECT_DIR, "locale"),
)

LANGUAGES = (
    ('en', _('English')),
    ('fr', _('French')),
    ('pt', _('Portuguese')),
)

DEFAULT_LANGUAGE = 'en'
