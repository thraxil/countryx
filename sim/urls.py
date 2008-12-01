from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
                       (r'^$', 'genocideprevention.sim.views.root'),
                       (r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'sim/logged_out.html'}),
                       (r'^narrative/(?P<group_id>\d+)/(?P<user_id>\d+)/$', 'genocideprevention.sim.views.narrative'),
                       (r'^decision/(?P<group_id>\d+)/(?P<user_id>\d+)/$', 'genocideprevention.sim.views.decision'),
                       (r'^section/(?P<section_id>\d+)/$', 'genocideprevention.sim.views.section'),
)