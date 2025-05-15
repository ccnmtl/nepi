from django.conf import settings
from nepi.settings_shared import (
    project, base, STATIC_ROOT, INSTALLED_APPS
)
from ctlsettings.production import common, init_sentry


locals().update(
    common(
        project=project,  # noqa: F405
        base=base,  # noqa: F405
        STATIC_ROOT=STATIC_ROOT,  # noqa: F405
        INSTALLED_APPS=INSTALLED_APPS,  # noqa: F405
        s3prefix='ccnmtl',
    ))


# Update the django-storages parameter
AWS_S3_OBJECT_PARAMETERS = {
    'ACL': 'public-read',
}


try:
    from nepi.local_settings import *  # noqa: F403 F401
except ImportError:
    pass


if hasattr(settings, 'SENTRY_DSN'):
    init_sentry(SENTRY_DSN)  # noqa F405
