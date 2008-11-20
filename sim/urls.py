from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
                       (r'^$', 'genocideprevention.sim.views.root'),
                       (r'^login/$', 'djangowind.views.login', {'template_name': 'sim/login.html'}),
                       (r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'sim/logged_out.html'}),
                       (r'^narrative/(?P<group_id>\d+)/(?P<player_id>\d+)/$', 'genocideprevention.sim.views.narrative'),
                       (r'^decision/(?P<group_id>\d+)/(?P<player_id>\d+)/$', 'genocideprevention.sim.views.decision'),
)