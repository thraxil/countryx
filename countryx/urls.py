from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView

import django.contrib.auth.views
import django.views.static
import countryx.sim.views

import os.path
admin.autodiscover()

site_media_root = os.path.join(
    os.path.dirname(__file__),
    "../media")

urlpatterns = [
    url(r'^$', countryx.sim.views.root),
    url(r'^accounts/logout/$',
        django.contrib.auth.views.logout, {'next_page': '/'}),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^impersonate/', include('impersonate.urls')),
    url(r'^sim/', include('countryx.sim.urls')),
    url(r'^smoketest/', include('smoketest.urls')),
    url('^stats/', TemplateView.as_view(template_name='stats.html')),
    url(r'^site_media/(?P<path>.*)$',
        django.views.static.serve, {'document_root': site_media_root}),
    url(r'^uploads/(?P<path>.*)$',
        django.views.static.serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^about', TemplateView.as_view(template_name='flatpages/about.html')),
    url(r'^help', TemplateView.as_view(template_name='flatpages/help.html')),
    url(r'^contact',
        TemplateView.as_view(template_name='flatpages/contact.html')),
]
