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
    SENTRY_SITE = 'countryx-staging'
    SENTRY_SERVERS = ['http://sentry.ccnmtl.columbia.edu/sentry/store/']

    import logging
    from raven.contrib.django.handlers import SentryHandler
    logger = logging.getLogger()
    # ensure we havent already registered the handler
    if SentryHandler not in map(type, logger.handlers):
        logger.addHandler(SentryHandler())
        logger = logging.getLogger('sentry.errors')
        logger.propagate = False
        logger.addHandler(logging.StreamHandler())


try:
    from local_settings import *
except ImportError:
    pass
