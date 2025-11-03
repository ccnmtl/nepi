# flake8: noqa
# Django settings for nepi project.
import os
import sys
from ctlsettings.shared import common
from django.utils.translation import gettext_lazy as _

project = 'nepi'
base = os.path.dirname(__file__)
locals().update(common(project=project, base=base))

# where the project codebase lives. eg, /var/www/myapp/myapp
PROJECT_DIR = os.path.normpath(os.path.join(base, "../"))

if 'test' in sys.argv or 'jenkins' in sys.argv:
    CAPTCHA_TEST_MODE = True

PROJECT_APPS = [
    'nepi.main',
    'nepi.activities',
]

ALLOWED_HOSTS += [
    'localhost',
    '.ccnmtl.columbia.edu',
    '.ctl.columbia.edu',
    'elearning.icap.columbia.edu',
]

USE_TZ = True
USE_I18N = True

MIDDLEWARE += [
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django_cas_ng.middleware.CASMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INSTALLED_APPS += [  # noqa
    'sorl.thumbnail',
    'bootstrap3',
    'debug_toolbar',
    'bootstrapform',
    'django_extensions',
    'nepi.main',
    'pagetree',
    'pageblocks',
    'quizblock',
    'captcha',
    'nepi.activities',
    'waffle',
    'markdownify.apps.MarkdownifyConfig',
]

PAGEBLOCKS = [
    'pageblocks.HTMLBlockWYSIWYG',
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
    'activities.AdherenceCard',
]

AUTH_PROFILE_MODULE = 'nepi.main.UserProfile'

ICAP_MAILING_LIST = 'ctl-dev@columbia.edu'
NEPI_MAILING_LIST = 'ctl-dev@columbia.edu'

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

# Translate CUIT's CAS user attributes to the Django user model.
# https://cuit.columbia.edu/content/cas-3-ticket-validation-response
CAS_APPLY_ATTRIBUTES_TO_USER = True
CAS_RENAME_ATTRIBUTES = {
    'givenName': 'first_name',
    'lastName': 'last_name',
    'mail': 'email',
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(base, "templates"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'stagingcontext.staging_processor',
                'gacontext.ga_processor',
                'django.template.context_processors.csrf',
                'nepi.main.views.context_processor'
            ],
        },
    },
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
