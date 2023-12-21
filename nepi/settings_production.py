from nepi.settings_shared import *  # noqa: F403
from ctlsettings.production import common


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
