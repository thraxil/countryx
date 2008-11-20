from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
                       (r'^$', 'genocideprevention.sim.views.root'),
                       (r'^login', 'djangowind.views.login'),
                       (r'^logout', 'django.contrib.auth.views.logout'),
                       (r'^narrative/(?P<group_id>\d+)/(?P<player_id>\d+)/$', 'genocideprevention.sim.views.narrative'),
                       (r'^decision/(?P<group_id>\d+)/(?P<player_id>\d+)/$', 'genocideprevention.sim.views.decision'),
)