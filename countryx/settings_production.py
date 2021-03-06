# flake8: noqa
from .settings_shared import *
import os

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), "templates"),
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
        'ATOMIC_REQUESTS': True,
        }
}

AWS_S3_CUSTOM_DOMAIN = 'd3pm8n47h5kmes.cloudfront.net'
AWS_STORAGE_BUCKET_NAME = "ccnmtl-countryx-static-prod"
AWS_PRELOAD_METADATA = True
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
S3_URL = 'https://%s/' % AWS_S3_CUSTOM_DOMAIN
# static data, e.g. css, js, etc.
STATICFILES_STORAGE = 'cacheds3storage.CompressorS3BotoStorage'
STATIC_URL = 'https://%s/media/' % AWS_S3_CUSTOM_DOMAIN
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_URL = STATIC_URL
COMPRESS_STORAGE = 'cacheds3storage.CompressorS3BotoStorage'

try:
    from local_settings import *
except ImportError:
    pass
