# flake8: noqa
# Django settings for nepi project.
import os
import sys
from ccnmtlsettings.shared import common
from django.utils.translation import ugettext_lazy as _

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

ALLOWED_HOSTS = [
    'localhost',
    '.ccnmtl.columbia.edu',
    'elearning.icap.columbia.edu',
]

USE_TZ = True
USE_I18N = True

MIDDLEWARE_CLASSES += [
    'django.middleware.locale.LocaleMiddleware',
]

TEMPLATE_CONTEXT_PROCESSORS += [  # noqa
    'nepi.main.views.context_processor',
]

INSTALLED_APPS += [  # noqa
    'sorl.thumbnail',
    'tagging',
    'typogrify',
    'bootstrapform',
    'django_extensions',
    'nepi.main',
    'pagetree',
    'pageblocks',
    'quizblock',
    'captcha',
    'nepi.activities',
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
