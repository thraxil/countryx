from settings_shared import *

TEMPLATE_DIRS = (
    "/var/www/countryx/countryx/templates",
)

MEDIA_ROOT = '/var/www/countryx/uploads/'

DEBUG = False
TEMPLATE_DEBUG = DEBUG
try:
    from local_settings import *
except ImportError:
    pass
