# flake8: noqa
from .settings_shared import *
import os
import os.path

from thraxilsettings.docker import common

locals().update(
    common(
        app=app,
        base=base,
        celery=False,
        INSTALLED_APPS=INSTALLED_APPS,
        STATIC_ROOT=STATIC_ROOT,
        MIDDLEWARE=MIDDLEWARE,
    ))
