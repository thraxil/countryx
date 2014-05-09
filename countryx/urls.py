from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
import os.path
admin.autodiscover()

site_media_root = os.path.join(
    os.path.dirname(__file__),
    "../media")
admin_media_root = os.path.join(
    os.path.dirname(__file__),
    "ve/lib/python2.6/site-packages/django/contrib/admin/media")

urlpatterns = patterns(
    '',
    (r'^$', 'countryx.sim.views.root'),
    ('^accounts/', include('djangowind.urls')),
    (r'^admin/', include(admin.site.urls)),
    url(r'^impersonate/', include('impersonate.urls')),
    (r'^sim/', include('countryx.sim.urls')),
    (r'^smoketest/$', include('smoketest.urls')),
    ('^stats/', TemplateView.as_view(template_name='stats.html')),
    (r'^site_media/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': site_media_root}),
    (r'^admin_media/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': admin_media_root}),
    (r'^uploads/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

urlpatterns += patterns(
    'django.views.generic.simple',
    (r'^about', TemplateView.as_view(template_name='flatpages/about.html')),
    (r'^help', TemplateView.as_view(template_name='flatpages/help.html')),
    (r'^contact',
     TemplateView.as_view(template_name='flatpages/contact.html')),
)
