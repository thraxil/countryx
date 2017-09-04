# Django settings for countryx project.
import os.path
import sys

DEBUG = True

ADMINS = (
    ('CCNMTL', 'ccnmtl-sysadmin@columbia.edu'),
)

MANAGERS = ADMINS

ALLOWED_HOSTS = [".ccnmtl.columbia.edu", "localhost"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'countryx',
        'HOST': '',
        'PORT': 5432,
        'USER': '',
        'PASSWORD': '',
        'ATOMIC_REQUESTS': True,
    }
}

if 'test' in sys.argv or 'jenkins' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'HOST': '',
            'PORT': '',
            'USER': '',
            'PASSWORD': '',
            'ATOMIC_REQUESTS': True,
        }
    }

TEST_RUNNER = 'django.test.runner.DiscoverRunner'
TEST_OUTPUT_DIR = 'reports'

PROJECT_APPS = ['countryx.sim', 'countryx.events']

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False
MEDIA_ROOT = "/var/www/countryx/uploads/"
MEDIA_URL = '/uploads/'
STATIC_URL = '/media/'
SECRET_KEY = 'dummy-)ng#)ef_u@_^zvvu@dxm7ql-yb^_!a6%v3v^j3b(mp+)l+5%@h'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(os.path.dirname(__file__), "templates"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

MIDDLEWARE_CLASSES = [
    'django_statsd.middleware.GraphiteRequestTimingMiddleware',
    'django_statsd.middleware.GraphiteMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'waffle.middleware.WaffleMiddleware',
    'impersonate.middleware.ImpersonateMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'countryx.urls'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'bootstrapform',
    'countryx.sim',
    'countryx.events',
    'django_statsd',
    'waffle',
    'impersonate',
    'django_markwhat',
    'compressor',
    'debug_toolbar',
]

INTERNAL_IPS = ('127.0.0.1', )
DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
)

STATSD_CLIENT = 'statsd.client'
STATSD_PREFIX = 'countryx'
STATSD_HOST = 'localhost'
STATSD_PORT = 8125

MEDIA_URL = "/uploads/"
MEDIA_ROOT = 'uploads'
STATIC_URL = "/media/"
STATIC_ROOT = "/tmp/countryx/static"
STATICFILES_DIRS = ('media/',)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
COMPRESS_URL = "/media/"
COMPRESS_ROOT = "media/"
AWS_QUERYSTRING_AUTH = False

THUMBNAIL_SUBDIR = "thumbs"
EMAIL_SUBJECT_PREFIX = "[countryx] "
EMAIL_HOST = 'localhost'
SERVER_EMAIL = "countryx@ccnmtl.columbia.edu"

STATE_COLORS = [
    'ffd478', '009192', 'ff9400', 'd25700', '935200', 'd4fb79',
    '73fa79', '8efa00', '4e8f00', '0096ff', '0a31ff', 'd783ff',
    '7a80ff', '531a93', 'ff8ad8', 'ff3092', 'ff40ff', '009051',
    '942092', '941751', '941200', 'ff2700', '005393', 'ff7e79',
    'fffc00', '76d6ff', '00f900', '929292', '929000']

LOGIN_REDIRECT_URL = "/"
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_HTTPONLY = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}
