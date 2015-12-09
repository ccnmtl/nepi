# flake8: noqa
import os
from settings_shared import *
from ccnmtlsettings.production import common

locals().update(
    common(
        project=project,
        base=base,
        INSTALLED_APPS=INSTALLED_APPS,
        STATIC_ROOT=STATIC_ROOT,
        s3static=False,
    ))

try:
    from local_settings import *
except ImportError:
    pass
