from django.conf.urls import patterns, url
import os.path
from .views import (
    CreateSectionView, DeleteSectionView,
    RolesIndexView, StatesIndexView, StateDetailView,
    RoleDetailView, DeleteRoleView, CreateRoleView,
    RoleUpdate, StateUpdate, StateDelete,
)

media_root = os.path.join(os.path.dirname(__file__), "media")

urlpatterns = patterns(
    '',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': media_root}),
    (r'^$', 'countryx.sim.views.root'),
    (r'^logout/$', 'django.contrib.auth.views.logout',
     {'template_name': 'sim/logged_out.html'}),

    # player pages
    (r'^player/game/(?P<group_id>\d+)/$', 'countryx.sim.views.player_game'),
    (r'^player/game/(?P<group_id>\d+)/(?P<turn_id>\d+)/$',
     'countryx.sim.views.player_game'),

    # player ajax requests
    (r'^player/choose/$', 'countryx.sim.views.player_choose'),

    # faculty ajax requests
    (r'^faculty/reset/(?P<section_id>\d+)/$',
     'countryx.sim.views.faculty_section_reset'),

    # faculty management pages
    (r'^allpaths/$', 'countryx.sim.views.allpaths'),
    (r'^allpaths/questions$', 'countryx.sim.views.allquestions'),
    (r'^allpaths/variables$', 'countryx.sim.views.allvariables'),
    (r'^faculty/manage/(?P<section_id>\d+)/$',
     'countryx.sim.views.faculty_section_manage'),
    (r'^faculty/manage/(?P<section_id>\d+)/end_turn/$',
     'countryx.sim.views.faculty_end_turn'),
    (r'^faculty/groups/(?P<section_id>\d+)/$',
     'countryx.sim.views.faculty_section_bygroup'),
    (r'^faculty/players/(?P<section_id>\d+)/$',
     'countryx.sim.views.faculty_section_byplayer'),
    (r'^faculty/group/(?P<group_id>\d+)/$',
     'countryx.sim.views.faculty_group_detail'),
    ((r'^faculty/player/turn/(?P<group_id>\d+)/'
      r'(?P<player_id>\d+)/(?P<state_id>\d+)/$'),
     'countryx.sim.views.faculty_player_detail_byturn'),
    (r'^faculty/player/(?P<player_id>\d+)/$',
     'countryx.sim.views.faculty_player_detail'),
    (r'^faculty/feedback/$', 'countryx.sim.views.faculty_feedback_submit'),
    url(r'^section/new/$', CreateSectionView.as_view(), name='create-section'),
    url(r'^section/(?P<pk>\d+)/delete/$', DeleteSectionView.as_view(),
        name='delete-section'),

    url(r'^roles/$', RolesIndexView.as_view(), name="roles-index"),
    url(r'^roles/add/$', CreateRoleView.as_view(), name="create-role"),
    url(r'^roles/(?P<pk>\d+)/$', RoleDetailView.as_view(), name="role"),
    url(r'^roles/(?P<pk>\d+)/delete/$', DeleteRoleView.as_view(),
        name="delete-role"),
    url(r'^roles/(?P<pk>\d+)/edit/$', RoleUpdate.as_view(),
        name="edit-role"),
    url(r'^states/$', StatesIndexView.as_view(), name="states-index"),
    url(r'^states/(?P<pk>\d+)/$', StateDetailView.as_view(), name="state"),
    url(r'^states/(?P<pk>\d+)/edit/$', StateUpdate.as_view(),
        name="edit-state"),
    url(r'^states/(?P<pk>\d+)/delete/$', StateDelete.as_view(),
        name="delete-state"),
)
