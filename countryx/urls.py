from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.views.generic import TemplateView

import django.contrib.auth.views
import django.views.static
import countryx.sim.views
import countryx.sim.urls
import countryx.events.urls
import countryx.reports.urls

admin.autodiscover()

urlpatterns = [
    url(r'^$', countryx.sim.views.root),
    url(r'^accounts/logout/$', LogoutView.as_view(next_page='/')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^impersonate/', include('impersonate.urls')),
    url(r'^sim/', include(countryx.sim.urls)),
    url(r'^smoketest/', include('smoketest.urls')),
    url('^stats/', TemplateView.as_view(template_name='stats.html')),
    url(r'^site_media/(?P<path>.*)$',
        django.views.static.serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^uploads/(?P<path>.*)$',
        django.views.static.serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^about', TemplateView.as_view(template_name='flatpages/about.html')),
    url(r'^help', TemplateView.as_view(template_name='flatpages/help.html')),
    url(r'^contact',
        TemplateView.as_view(template_name='flatpages/contact.html')),
    url(r'^events/', include(countryx.events.urls)),
    url(r'^reports/', include(countryx.reports.urls)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
