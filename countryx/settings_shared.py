# Django settings for countryx project.
import os.path
import sys

DEBUG = True
TEMPLATE_DEBUG = DEBUG

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
        }
    }

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    'countryx',
    'countryx.sim',
    '--with-coverage',
    '--cover-package=countryx',
]

JENKINS_TASKS = (
    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.run_pyflakes',
)

PROJECT_APPS = ['countryx.sim', ]

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False
MEDIA_ROOT = "/var/www/countryx/uploads/"
MEDIA_URL = '/uploads/'
STATIC_URL = '/media/'
SECRET_KEY = 'dummy-)ng#)ef_u@_^zvvu@dxm7ql-yb^_!a6%v3v^j3b(mp+)l+5%@h'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'stagingcontext.staging_processor',
    'djangowind.context.context_processor',
    'gacontext.ga_processor',
)

MIDDLEWARE_CLASSES = (
    'django_statsd.middleware.GraphiteRequestTimingMiddleware',
    'django_statsd.middleware.GraphiteMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'waffle.middleware.WaffleMiddleware',
    'impersonate.middleware.ImpersonateMiddleware',
    'countryx.sim.middleware.GameStateMiddleware',
)

ROOT_URLCONF = 'countryx.urls'

TEMPLATE_DIRS = (
    "/var/www/countryx/templates/",
    os.path.join(os.path.dirname(__file__), "templates"),
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'countryx.sim',
    'django_statsd',
    'django_nose',
    'south',
    'raven.contrib.django',
    'django_jenkins',
    'waffle',
    'impersonate',
    'django_markwhat',
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

SOUTH_TESTS_MIGRATE = False

STATSD_CLIENT = 'statsd.client'
STATSD_PREFIX = 'countryx'
STATSD_HOST = 'localhost'
STATSD_PORT = 8125

STATIC_URL = "/media/"
STATICFILES_DIRS = (
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../media/")),
)
STATIC_ROOT = ""
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


THUMBNAIL_SUBDIR = "thumbs"
EMAIL_SUBJECT_PREFIX = "[countryx] "
EMAIL_HOST = 'localhost'
SERVER_EMAIL = "countryx@ccnmtl.columbia.edu"

# WIND settings

AUTHENTICATION_BACKENDS = ('djangowind.auth.SAMLAuthBackend',
                           'django.contrib.auth.backends.ModelBackend',)
CAS_BASE = "https://cas.columbia.edu/"

WIND_PROFILE_HANDLERS = ['djangowind.auth.CDAPProfileHandler']
WIND_AFFIL_HANDLERS = ['djangowind.auth.AffilGroupMapper',
                       'djangowind.auth.StaffMapper',
                       'djangowind.auth.SuperuserMapper']
WIND_STAFF_MAPPER_GROUPS = ['tlc.cunix.local:columbia.edu']
WIND_SUPERUSER_MAPPER_GROUPS = ['anp8', 'jb2410', 'zm4', 'sld2131']
LOGIN_REDIRECT_URL = "/"
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_HTTPONLY = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}
