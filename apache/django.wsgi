import os, sys, site

# enable the virtualenv
site.addsitedir('/var/www/genocideprevention/genocideprevention/ve/lib/python2.5/site-packages')

# paths we might need to pick up the project's settings
sys.path.append('/var/www/')
sys.path.append('/var/www/genocideprevention/')
sys.path.append('/var/www/genocideprevention/genocideprevention/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'genocideprevention.settings_production'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
