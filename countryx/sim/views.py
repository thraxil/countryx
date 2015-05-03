from annoying.decorators import render_to
from countryx.sim.models import Role
from countryx.sim.models import SectionAdministrator, Section
from countryx.sim.models import SectionGroupPlayer
from countryx.sim.models import SectionGroup
from countryx.sim.models import State, SectionGroupPlayerTurn
from countryx.sim.models import StateChange
from countryx.sim.models import StateRoleChoice
from countryx.sim.models import StateVariable
from countryx.sim.models import SectionGroupState
from countryx.sim.models import num_turns
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import View, ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django import forms
import datetime
import json
from django.http import Http404


class StaffOnlyMixin(object):
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super(StaffOnlyMixin, self).dispatch(*args, **kwargs)


@login_required
def root(request):
    if (request.user.is_staff):
        return __faculty_index(request)
    else:
        return __player_index(request)

###############################################################################
###############################################################################


@render_to("sim/faculty_index.html")
def __faculty_index(request):
    sections = Section.objects.filter(sectionadministrator__user=request.user)
    roles = Role.objects.all()
    return dict(sections=sections, user=request.user, roles=roles)


class CreateSectionView(StaffOnlyMixin, View):
    def post(self, request):
        # first, make sure no usernames are duplicated
        now = datetime.datetime.now()
        s = Section.objects.create(
            name=request.POST.get('section_name', 'unamed section'),
            turn=1,
            created_date=now)
        SectionAdministrator.objects.create(section=s, user=request.user)
        for i in range(num_turns() + 1):
            group_name = request.POST.get('group_name_%d' % i, '').strip()
            if not group_name:
                continue
            sg = SectionGroup.objects.create(section=s, name=group_name)
            for r in Role.objects.all():
                username = request.POST.get('group_%d_username_%d' % (i, r.id))
                password = request.POST.get('group_%d_password_%d' % (i, r.id))
                if User.objects.filter(username=username).exists():
                    u = User.objects.get(username=username)
                else:
                    u = User.objects.create(
                        username=username,
                        last_name=username,
                    )
                u.set_password(password)
                u.save()
                SectionGroupPlayer.objects.create(
                    user=u,
                    role=r,
                    group=sg,
                )
            s.reset_sectiongroupstates()
        return HttpResponseRedirect("/sim/")


class DeleteSectionView(StaffOnlyMixin, DeleteView):
    model = Section
    success_url = "/sim/"


class RolesIndexView(StaffOnlyMixin, ListView):
    model = Role


class StatesIndexView(StaffOnlyMixin, ListView):
    model = State


class StateDetailView(StaffOnlyMixin, DetailView):
    model = State


class RoleDetailView(StaffOnlyMixin, DetailView):
    model = Role


class CreateRoleView(StaffOnlyMixin, CreateView):
    model = Role


class DeleteRoleView(StaffOnlyMixin, DeleteView):
    model = Role

    def get_success_url(self):
        return reverse('roles-index')


class RoleUpdate(StaffOnlyMixin, UpdateView):
    model = Role
    fields = ['description']
    template_name = "sim/role_edit_form.html"


class StateUpdate(StaffOnlyMixin, UpdateView):
    model = State
    fields = ['name', 'turn', 'state_no', 'description']
    template_name = "sim/state_edit_form.html"


class StateDelete(StaffOnlyMixin, DeleteView):
    model = State

    def get_success_url(self):
        return reverse('states-index')


class StateChangeDelete(StaffOnlyMixin, DeleteView):
    model = StateChange

    def get_success_url(self):
        return reverse('state', args=(self.object.state.id,))


class StateCreate(StaffOnlyMixin, CreateView):
    model = State


class StateAddRoleChoice(StaffOnlyMixin, View):
    template_name = "sim/state_add_role_choice.html"

    def get(self, request, pk):
        state = get_object_or_404(State, id=pk)
        selected = request.GET.get('role')
        return render(
            request,
            self.template_name,
            dict(state=state,
                 selected=selected,
                 roles=Role.objects.all()))

    def post(self, request, pk):
        state = get_object_or_404(State, id=pk)
        role = get_object_or_404(Role, id=request.POST.get('role'))
        choice = int(request.POST.get('choice', '1'))
        desc = request.POST.get('description', '')
        StateRoleChoice.objects.create(
            state=state,
            role=role,
            choice=choice,
            desc=desc
        )
        return HttpResponseRedirect(reverse('state', args=(pk,)))


class StateAddStateChange(StaffOnlyMixin, View):
    template_name = "sim/state_add_statechange.html"

    def get(self, request, pk):
        state = get_object_or_404(State, id=pk)
        return render(
            request,
            self.template_name,
            dict(state=state))

    def post(self, request, pk):
        state = get_object_or_404(State, id=pk)
        next_state = get_object_or_404(
            State, id=request.POST.get('next_state'))

        roles = dict()
        for role in Role.objects.all():
            roles[role.name] = request.POST.get("role_%s" % role.name)

        StateChange.objects.create(
            state=state,
            next_state=next_state,
            roles=json.dumps(roles)
        )
        return HttpResponseRedirect(reverse('state', args=(pk,)))


class StateRoleChoiceDelete(StaffOnlyMixin, DeleteView):
    model = StateRoleChoice

    def get_success_url(self):
        return reverse('state', args=(self.object.state.id,))


@login_required
@render_to("sim/faculty_section_bygroup.html")
def faculty_section_bygroup(request, section_id):
    return dict(user=request.user, section=Section.objects.get(id=section_id))


@login_required
@render_to('sim/faculty_section_byplayer.html')
def faculty_section_byplayer(request, section_id):
    section = Section.objects.get(id=section_id)
    all_players = SectionGroupPlayer.objects.select_related().filter(
        group__section=section)
    return {
        'user': request.user,
        'section': section,
        'players': all_players,
    }


@login_required
def faculty_section_reset(request, section_id):
    response = {}

    if not request.user.is_superuser:
        response['message'] = "Access denied"
    else:
        section = get_object_or_404(Section, id=section_id)
        section.reset()

    return HttpResponse(json.dumps(response), 'application/json')


@login_required
@render_to('sim/faculty_group_detail.html')
def faculty_group_detail(request, group_id):
    group = SectionGroup.objects.get(id=group_id)

    turns = []

    # for each completed state, list the players and their choices
    group_states = group.sectiongroupstate_set.order_by('-date_updated')
    for gs in group_states:
        # for each player, setup their actions
        player_turns = []

        players = group.sectiongroupplayer_set.all()
        for p in players:
            try:
                turn = SectionGroupPlayerTurn.objects.get(
                    player=p, turn=gs.state.turn)
            except SectionGroupPlayerTurn.DoesNotExist:
                turn = None

            player_turns.append(
                {
                    'model': p,
                    'turn': turn,
                    'submit_status': p.status(gs.state)
                })

        conditions = gs.state.country_condition()
        turns.append(
            {
                'group_state': gs,
                'players': player_turns,
                'country_condition': conditions
            })

    return dict(user=request.user,
                group=group,
                turns=turns,
                section=group.section,
                )


@login_required
@render_to('sim/faculty_player_detail_byturn.html')
def faculty_player_detail_byturn(request, group_id, player_id,
                                 state_id, updated=False):
    group = get_object_or_404(SectionGroup, id=group_id)
    player = get_object_or_404(SectionGroupPlayer, id=player_id, group=group)
    state = get_object_or_404(State, id=state_id)
    turn = get_object_or_404(SectionGroupPlayerTurn,
                             player=player, turn=state.turn)

    return dict(
        user=request.user,
        group=group,
        section=group.section,
        player=player,
        state=state,
        turn=turn,
        submit_status=player.status(state),
        choices=StateRoleChoice.objects.filter(state=state, role=player.role),
        country_condition=state.country_condition(),
        form=FeedbackForm(initial={'faculty_id': request.user.id,
                                   'feedback': turn.feedback,
                                   'turn_id': state.turn}),
        updated=updated
    )


@login_required
@render_to('sim/faculty_player_detail.html')
def faculty_player_detail(request, player_id):
    player = get_object_or_404(SectionGroupPlayer, id=player_id)
    group = player.group

    player_turns = []
    turns = SectionGroupPlayerTurn.objects.filter(
        player=player).order_by("-turn")

    for t in turns:
        turn_state = group.sectiongroupstate_set.get(state__turn=t.turn).state
        player_turn = {
            'turn': t.turn,
            'submit_status': player.status(turn_state),
            'choice': t.choice,
            'choices': StateRoleChoice.objects.filter(
                state=turn_state, role=player.role),
            'country_condition': turn_state.country_condition(),
            'submit_date': t.submit_date,
            'reasoning': t.reasoning,
            'state': turn_state,
            'automatic_update': t.automatic_update,
            'form': FeedbackForm(
                initial={
                    'faculty_id': request.user.id,
                    'feedback': t.feedback,
                    'turn_id': t.turn}),
        }

        player_turns.append(player_turn)

    return dict(user=request.user,
                player=player,
                group=group,
                section=group.section,
                player_turns=player_turns,
                )


def faculty_feedback_submit(request):
    response = {}
    player_id = request.POST.get('player_id', None)
    faculty_id = int(request.POST.get('faculty_id', None))
    turn_id = int(request.POST.get('turn_id', None))
    feedback = request.POST.get('feedback', '')
    player = get_object_or_404(SectionGroupPlayer, id=player_id)
    group = player.group

    # Retrieve the associated player turn to update
    turn = get_object_or_404(SectionGroupPlayerTurn, player=player,
                             turn=turn_id)

    turn.feedback = feedback
    turn.feedback_date = datetime.datetime.now()
    turn.faculty = get_object_or_404(SectionAdministrator,
                                     section=group.section,
                                     user__id=faculty_id)
    turn.save()

    response['result'] = 1
    response['turn_id'] = turn_id
    response['message'] = "Your feedback has been saved."
    return HttpResponse(json.dumps(response), 'application/json')


class FeedbackForm(forms.Form):
    feedback = forms.CharField(widget=forms.Textarea)
    faculty_id = forms.IntegerField(widget=forms.HiddenInput)
    turn_id = forms.IntegerField(widget=forms.HiddenInput)


@login_required
def faculty_end_turn(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    section.end_turn()
    section.ensure_consistency()
    return HttpResponseRedirect("/sim/")


@login_required
def faculty_section_manage(request, section_id, updated=False):
    section = get_object_or_404(Section, id=section_id)

    return render(
        request,
        'sim/faculty_section_manage.html', {
            'user': request.user,
            'section': section,
            'updated': updated
        })

EMPTY_VALUES = (None, '')


class DateTimeFieldEx(forms.DateTimeField):
    def clean(self, value):
        if (not self.required and
                value[0] in EMPTY_VALUES and
                value[1] in EMPTY_VALUES):
            return None
        return super(DateTimeFieldEx, self).clean(value)


###############################################################################
###############################################################################


@render_to("sim/player_index.html")
def __player_index(request):
    groups = SectionGroup.objects.filter(sectiongroupplayer__user=request.user)
    return dict(user=request.user, groups=groups)


def tab_name(i):
    if i < num_turns():
        return 'Phase %s' % i
    else:
        return "Results"


def tab_viewable(group, i):
    try:
        group.sectiongroupstate_set.get(state__turn=i).state
        return True
    except:
        return False


@render_to('sim/player_game.html')
@login_required
def player_game(request, group_id, turn_id=0):
    group = get_object_or_404(SectionGroup, id=group_id)

    if turn_id == 0:
        try:
            working_state = group.sectiongroupstate_set.latest().state
        except SectionGroupState.DoesNotExist:
            # put them in the start state automatically
            start_state = State.objects.get(turn=1, state_no=1)
            SectionGroupState.objects.create(
                group=group,
                state=start_state,
                date_updated=datetime.datetime.now())
            working_state = start_state
    else:
        working_state = group.sectiongroupstate_set.get(
            state__turn=turn_id).state

    tabs = [dict(id=i, activetab=(working_state.turn == i),
                 viewable=tab_viewable(group, i), name=tab_name(i),
                 ) for i in range(1, num_turns() + 1)]

    # setup set of special attributes for current user
    your_player = {
        'model': group.sectiongroupplayer_set.get(
            user__id=request.user.id),
        'saved_turn': None,
        'saved_choice': None}
    your_player['submit_status'] = your_player['model'].status(working_state)
    your_player['choices'] = StateRoleChoice.objects.filter(
        state=working_state, role=your_player['model'].role)

    try:
        your_player['saved_turn'] = SectionGroupPlayerTurn.objects.get(
            player=your_player['model'], turn=working_state.turn)
        your_player['saved_choice'] = StateRoleChoice.objects.get(
            state=working_state, role=your_player['model'].role,
            choice=your_player['saved_turn'].choice)
    except SectionGroupPlayerTurn.DoesNotExist:
        your_player['saved_turn'] = None

    endgame_results = []
    feedback = None
    if working_state.turn == num_turns():
        turns = SectionGroupPlayerTurn.objects.filter(
            player=your_player['model']).order_by('turn')
        endgame_results = zip(turns, tabs)
        feedback = SectionGroupPlayerTurn.objects.get(
            player=your_player['model'], turn=3).feedback

    # setup player list attributes
    players = [dict(model=p, submit_status=p.status(working_state))
               for p in group.sectiongroupplayer_set.all()
               if (p != your_player['model'])]
    return dict(
        user=request.user,
        group=group,
        state=working_state,
        country_condition=working_state.country_condition(),
        tabs=tabs,
        players=players,
        you=your_player,
        endgame_results=endgame_results,
        feedback=feedback,
    )


# actually needs to be faculty only
@login_required
def allquestions(request):
    response = {}
    for x in StateRoleChoice.objects.all():
        response.setdefault(
            x.state.id,
            {}).setdefault(x.role.name, {}).setdefault(x.choice, x.desc)
    return HttpResponse(json.dumps(response), 'application/json')


# actually needs to be faculty only
@login_required
def allvariables(request):
    response = {}
    for x in StateVariable.objects.all():
        response.setdefault(x.state.id, {}).setdefault(x.name, x.value)
    return HttpResponse(json.dumps(response), 'application/json')


@render_to('sim/allpaths.html')
@login_required
def allpaths(request):
    turns = []
    roles = [r.name for r in Role.objects.all()]
    # NOTE: indexed at 1
    for turn in range(1, num_turns() + 1):
        states = State.objects.filter(turn=turn).order_by("state_no")
        turn = dict(
            states=[
                {
                    'id': s.id,
                    'state_no': s.state_no,
                    'name': s.name,
                    'full_from': s.full_from(roles),
                    'full_to': s.full_to(roles),
                    'color': s.get_color(),
                }
                for s in states
            ]
        )
        turns.append(turn)

    return dict(turns=turns, roles=roles)


@login_required
def player_choose(request):
    response = {}

    groupid = request.POST.get('groupid', None)
    choiceid = request.POST.get('choiceid', None)
    final = int(request.POST.get('final', False))
    reasoning = request.POST.get('reasoning', '')

    group = get_object_or_404(SectionGroup, id=groupid)
    try:
        player = group.sectiongroupplayer_set.get(user__id=request.user.id,
                                                  group=group)
    except SectionGroupPlayer.DoesNotExist:
        raise Http404
    current_state = group.sectiongroupstate_set.latest().state

    # create or update the player's choice
    turnList = SectionGroupPlayerTurn.objects.filter(player=player,
                                                     turn=current_state.turn)
    if len(turnList) > 0:
        turn = turnList[0]
    else:
        turn = SectionGroupPlayerTurn.objects.create(player=player,
                                                     turn=current_state.turn)

    if turn.submit_date is not None:
        # player has already submitted data
        response['result'] = 0
        response['message'] = 'Player has already submitted a final choice'
    else:
        turn.choice = choiceid
        turn.reasoning = reasoning
        if final:
            turn.submit_date = datetime.datetime.now()
        turn.save()

        if (final):
            response['result'] = 2
            response['message'] = ("Your choice and reasoning have "
                                   "been submitted")
        else:
            response['result'] = 1
            response['message'] = "Draft has been saved"

    return HttpResponse(json.dumps(response), 'application/json')


class FeedbackForm(forms.Form):
    feedback = forms.CharField(widget=forms.Textarea)
    faculty_id = forms.IntegerField(widget=forms.HiddenInput)
    turn_id = forms.IntegerField(widget=forms.HiddenInput)
