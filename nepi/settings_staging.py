# flake8: noqa
from nepi.settings_shared import *
from ccnmtlsettings.staging import common

locals().update(
    common(
        project=project,
        base=base,
        STATIC_ROOT=STATIC_ROOT,
        INSTALLED_APPS=INSTALLED_APPS
    ))

try:
    from nepi.local_settings import *
except ImportError:
    pass
