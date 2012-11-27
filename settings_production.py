from settings_shared import *

TEMPLATE_DIRS = (
    "/var/www/countryx/countryx/templates",
)

MEDIA_ROOT = '/var/www/countryx/uploads/'

DEBUG = False
TEMPLATE_DEBUG = DEBUG

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

try:
    from local_settings import *
except ImportError:
    pass
