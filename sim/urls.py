from django.conf.urls.defaults import *
from django.conf import settings
import os.path

media_root = os.path.join(os.path.dirname(__file__),"media")

urlpatterns = patterns('',
                       (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': media_root}),
                       (r'^$', 'genocideprevention.sim.views.root'),
                       (r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'sim/logged_out.html'}),
                       
                       # player pages
                       (r'^player/game/(?P<group_id>\d+)/$', 'genocideprevention.sim.views.player_game'),
                       (r'^player/game/(?P<group_id>\d+)/(?P<turn_id>\d+)/$', 'genocideprevention.sim.views.player_game'),
                       
                       # player ajax requests
                       (r'^player/choose/$', 'genocideprevention.sim.views.player_choose'),
                       
                       # faculty management pages
                       (r'^faculty/section/(?P<section_id>\d+)/$', 'genocideprevention.sim.views.faculty_section'),
                       #(r'^faculty/group/(?P<group_id>\d+)/$', 'genocideprevention.sim.views.faculty_group'),
                       (r'^faculty/player/(?P<section_id>\d+)/(?P<group_id>\d+)/(?P<player_id>\d+)/$', 'genocideprevention.sim.views.faculty_player'),
)