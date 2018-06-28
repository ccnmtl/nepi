# flake8: noqa
from nepi.settings_shared import *

try:
    from nepi.local_settings import *
except ImportError:
    pass
