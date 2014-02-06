# flake8: noqa
from settings_shared import *

TEMPLATE_DIRS = (
    "/var/www/countryx/countryx/countryx/templates",
)

MEDIA_ROOT = '/var/www/countryx/uploads/'

DEBUG = False
TEMPLATE_DEBUG = DEBUG
STAGING_ENV = True

DATABASES = {
    'default' : {
        'ENGINE' : 'django.db.backends.postgresql_psycopg2',
        'NAME' : 'countryx',
        'HOST' : '',
        'PORT' : 6432,
        'USER' : '',
        'PASSWORD' : '',
        }
}
STATSD_PREFIX = 'countryx-staging'

if 'migrate' not in sys.argv:
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')

try:
    from local_settings import *
except ImportError:
    pass
