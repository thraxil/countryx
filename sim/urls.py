from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
                       (r'^$', 'genocideprevention.sim.views.root'),
                       (r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'sim/logged_out.html'}),
                       (r'^player/narrative/(?P<group_id>\d+)/(?P<user_id>\d+)/$', 'genocideprevention.sim.views.narrative'),
                       (r'^player/decision/(?P<group_id>\d+)/(?P<user_id>\d+)/$', 'genocideprevention.sim.views.decision'),
                       (r'^faculty/section/(?P<section_id>\d+)/$', 'genocideprevention.sim.views.faculty_section'),
                       (r'^faculty/player/(?P<section_id>\d+)/(?P<group_id>\d+)/(?P<player_id>\d+)/$', 'genocideprevention.sim.views.faculty_player'),
)