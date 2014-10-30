import os, sys, site

# paths we might need to pick up the project's settings
sys.path.append('/var/www/countryx/countryx/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'countryx.settings_staging'

import django.core.handlers.wsgi
import django
django.setup()
application = django.core.handlers.wsgi.WSGIHandler()
