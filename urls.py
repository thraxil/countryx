from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
import os.path
admin.autodiscover()

site_media_root = os.path.join(os.path.dirname(__file__),"media")
admin_media_root = os.path.join(os.path.dirname(__file__), "ve/lib/python2.5/site-packages/Django-1.0_final-py2.5.egg/django/contrib/admin/media")

urlpatterns = patterns('',
                       (r'^$', 'genocideprevention.views.root'),
                       ('^accounts/',include('djangowind.urls')),
                       (r'^admin/(.*)', admin.site.root),
                       (r'^sim/', include('genocideprevention.sim.urls')),
                       (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': site_media_root}),
                       (r'^admin_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': admin_media_root}),
                       (r'^uploads/(?P<path>.*)$','django.views.static.serve',{'document_root' : settings.MEDIA_ROOT}),
)