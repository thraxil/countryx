from django.conf.urls import url
from django.contrib.auth.views import LogoutView
import django.views.static
import os.path
from .views import (
    CreateSectionView, DeleteSectionView,
    RolesIndexView, StatesIndexView, StateDetailView,
    RoleDetailView, DeleteRoleView, CreateRoleView,
    RoleUpdate, StateUpdate, StateDelete,
    StateCreate, StateAddRoleChoice, StateRoleChoiceDelete,
    StateChangeDelete, StateAddStateChange,

    root, player_game, player_choose, faculty_section_reset,
    allpaths, allquestions, allvariables, faculty_section_manage,
    faculty_end_turn, faculty_section_bygroup, faculty_section_byplayer,
    faculty_group_detail, faculty_player_detail, faculty_feedback_submit,
    faculty_player_detail_byturn,
)

media_root = os.path.join(os.path.dirname(__file__), "media")

urlpatterns = [
    url(r'^media/(?P<path>.*)$', django.views.static.serve,
        {'document_root': media_root}),
    url(r'^$', root),
    url(r'^logout/$', LogoutView.as_view(
        template_name='sim/logged_out.html')),

    # player pages
    url(r'^player/game/(?P<group_id>\d+)/$', player_game),
    url(r'^player/game/(?P<group_id>\d+)/(?P<turn_id>\d+)/$', player_game),

    # player ajax requests
    url(r'^player/choose/$', player_choose),

    # faculty ajax requests
    url(r'^faculty/reset/(?P<section_id>\d+)/$', faculty_section_reset),

    # faculty management pages
    url(r'^allpaths/$', allpaths),
    url(r'^allpaths/questions$', allquestions),
    url(r'^allpaths/variables$', allvariables),
    url(r'^faculty/manage/(?P<section_id>\d+)/$', faculty_section_manage),
    url(r'^faculty/manage/(?P<section_id>\d+)/end_turn/$', faculty_end_turn),
    url(r'^faculty/groups/(?P<section_id>\d+)/$', faculty_section_bygroup),
    url(r'^faculty/players/(?P<section_id>\d+)/$', faculty_section_byplayer),
    url(r'^faculty/group/(?P<group_id>\d+)/$', faculty_group_detail),
    url((r'^faculty/player/turn/(?P<group_id>\d+)/'
         r'(?P<player_id>\d+)/(?P<state_id>\d+)/$'),
        faculty_player_detail_byturn),
    url(r'^faculty/player/(?P<player_id>\d+)/$', faculty_player_detail),
    url(r'^faculty/feedback/$', faculty_feedback_submit),
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
    url(r'^states/add/$', StateCreate.as_view(), name="create-state"),
    url(r'^states/(?P<pk>\d+)/$', StateDetailView.as_view(), name="state"),
    url(r'^states/(?P<pk>\d+)/edit/$', StateUpdate.as_view(),
        name="edit-state"),
    url(r'^states/(?P<pk>\d+)/delete/$', StateDelete.as_view(),
        name="delete-state"),
    url(r'^states/(?P<pk>\d+)/add_role_choice/$', StateAddRoleChoice.as_view(),
        name="add-role-choice"),
    url(r'^states/(?P<pk>\d+)/add_statechange/$',
        StateAddStateChange.as_view(),
        name="add-statechange"),
    url(r'^staterolechoice/(?P<pk>\d+)/delete/$',
        StateRoleChoiceDelete.as_view(),
        name="delete-role-choice"),
    url(r'^statechange/(?P<pk>\d+)/delete/$',
        StateChangeDelete.as_view(),
        name="delete-statechange"),
]
