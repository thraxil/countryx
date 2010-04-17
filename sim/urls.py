from django.conf.urls.defaults import *
from django.conf import settings
import os.path

media_root = os.path.join(os.path.dirname(__file__),"media")

urlpatterns = patterns('',
                       (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': media_root}),
                       (r'^$', 'countryx.sim.views.root'),
                       (r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'sim/logged_out.html'}),
                       
                       # player pages
                       (r'^player/game/(?P<group_id>\d+)/$', 'countryx.sim.views.player_game'),
                       (r'^player/game/(?P<group_id>\d+)/(?P<turn_id>\d+)/$', 'countryx.sim.views.player_game'),
                       
                       # player ajax requests
                       (r'^player/choose/$', 'countryx.sim.views.player_choose'),
                       
                       # faculty ajax requests
                       (r'^faculty/reset/(?P<section_id>\d+)/$', 'countryx.sim.views.faculty_section_reset'),
                       
                       # faculty management pages
                       (r'^allpaths/$', 'countryx.sim.views.allpaths'),
                       (r'^allpaths/questions$', 'countryx.sim.views.allquestions'),
                       (r'^allpaths/variables$', 'countryx.sim.views.allvariables'),
                       (r'^faculty/manage/(?P<section_id>\d+)/$', 'countryx.sim.views.faculty_section_manage'),
                       (r'^faculty/manage/(?P<section_id>\d+)/end_turn/$', 'countryx.sim.views.faculty_end_turn'),
                       (r'^faculty/groups/(?P<section_id>\d+)/$', 'countryx.sim.views.faculty_section_bygroup'),
                       (r'^faculty/players/(?P<section_id>\d+)/$', 'countryx.sim.views.faculty_section_byplayer'),
                       (r'^faculty/group/(?P<group_id>\d+)/$', 'countryx.sim.views.faculty_group_detail'),
                       
                       
                       (r'^faculty/player/turn/(?P<group_id>\d+)/(?P<player_id>\d+)/(?P<state_id>\d+)/$', 'countryx.sim.views.faculty_player_detail_byturn'),
                       (r'^faculty/player/(?P<player_id>\d+)/$', 'countryx.sim.views.faculty_player_detail'),
                       (r'^faculty/feedback/$', 'countryx.sim.views.faculty_feedback_submit'),

                       (r'^cheat/$', 'countryx.sim.views.cheat'),
                       (r'^check_statechanges/$', 'countryx.sim.views.check_statechanges'),
)
