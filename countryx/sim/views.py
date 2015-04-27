from annoying.decorators import render_to
from countryx.sim.models import Role
from countryx.sim.models import SectionAdministrator, Section
from countryx.sim.models import SectionGroupPlayer
from countryx.sim.models import SectionGroup, SectionTurnDates
from countryx.sim.models import State, SectionGroupPlayerTurn
from countryx.sim.models import StateRoleChoice
from countryx.sim.models import StateChange, StateVariable
from countryx.sim.models import SectionGroupState
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.generic import View
from django import forms
from django.forms.util import ErrorList
from django.contrib.admin.widgets import AdminSplitDateTime
import datetime
import json
from django.http import Http404


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


class CreateSectionView(View):
    def post(self, request):
        now = datetime.datetime.now()
        s = Section.objects.create(
            name=request.POST.get('name', 'unamed section'),
            created_date=now)
        SectionAdministrator.objects.create(section=s, user=request.user)
        SectionTurnDates.objects.create(
            section=s,
            turn1=now + datetime.timedelta(hours=100),
            turn2=now + datetime.timedelta(hours=200),
            turn3=now + datetime.timedelta(hours=300),
        )
        sg = SectionGroup.objects.create(section=s, name=s.name)
        for r in Role.objects.all():
            username = request.POST.get('username_%d' % r.id)
            password = request.POST.get('password_%d' % r.id)
            u = User.objects.create(username=username)
            u.set_password(password)
            u.save()
            SectionGroupPlayer.objects.create(
                user=u,
                role=r,
                group=sg,
            )
        s.reset_sectiongroupstates()
        return HttpResponseRedirect("/sim/")


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

        tm = SectionTurnDates.objects.get(section=section)
        response['turn1'] = tm.turn1.ctime()
        response['turn2'] = tm.turn2.ctime()
        response['turn3'] = tm.turn3.ctime()

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

        conditions = gs.state.statevariable_set.get(
            name='Country Condition').value
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
        country_condition=state.statevariable_set.get(
            name='Country Condition').value,
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
            'country_condition': turn_state.statevariable_set.get(
                name='Country Condition').value,
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
    return HttpResponseRedirect(request.META.get('HTTP_REFERER',
                                                 section.get_absolute_url()))


@login_required
def faculty_section_manage(request, section_id, updated=False):
    section = get_object_or_404(Section, id=section_id)

    if (request.method == 'POST'):
        form = TurnManagementForm(request.POST)
        if (form.is_valid()):
            # Process the data in form.cleaned_data
            try:
                tm = SectionTurnDates.objects.get(section=section)
            except SectionTurnDates.DoesNotExist:
                tm = SectionTurnDates.objects.create(
                    section=section, turn1=datetime.datetime.now())

            section.name = form.cleaned_data['section_name']
            section.save()

            tm.turn1 = form.cleaned_data['turn1']
            tm.turn2 = form.cleaned_data['turn2']
            tm.turn3 = form.cleaned_data['turn3']

            tm.save()

            redirect_url = '/sim/faculty/manage/%s/' % (section_id)
            return HttpResponseRedirect(redirect_url)
    else:
        initial = {}
        initial['section_name'] = section.name

        try:
            tm = SectionTurnDates.objects.get(section=section)
            initial['turn1'] = tm.turn1
            initial['turn2'] = tm.turn2
            initial['turn3'] = tm.turn3
        except SectionTurnDates.DoesNotExist:
            initial['turn1'] = datetime.datetime.now()

        form = TurnManagementForm(initial=initial)

    return render(
        request,
        'sim/faculty_section_manage.html', {
            'user': request.user,
            'section': section,
            'form': form,
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


class TurnManagementForm(forms.Form):
    section_name = forms.CharField()

    turn1 = DateTimeFieldEx(
        widget=AdminSplitDateTime, required=True, label="Turn 1 Close Date")
    turn2 = DateTimeFieldEx(
        widget=AdminSplitDateTime, required=False, label="Turn 2 Close Date")
    turn3 = DateTimeFieldEx(
        widget=AdminSplitDateTime, required=False, label="Turn 3 Close Date")

    def __compare(self, cleaned_data, fieldOne, fieldTwo, labelOne, labelTwo):
        if (fieldTwo in cleaned_data and
                not cleaned_data[fieldTwo] in EMPTY_VALUES):
            if (fieldOne in cleaned_data and
                not cleaned_data[fieldOne] in EMPTY_VALUES and
                cmp(cleaned_data[fieldOne],
                    cleaned_data[fieldTwo]) > -1):
                msg = "%s close date must be after %s close date" % (
                    labelTwo, labelOne)
                self._errors[fieldTwo] = ErrorList([msg])
                del cleaned_data[fieldTwo]

    def clean(self):
        cleaned_data = self.cleaned_data

        self.__compare(cleaned_data, "turn1", "turn2", "Turn 1", "Turn 2")
        self.__compare(cleaned_data, "turn1", "turn3", "Turn 1", "Turn 3")
        self.__compare(cleaned_data, "turn2", "turn3", "Turn 2", "Turn 3")

        return cleaned_data

###############################################################################
###############################################################################


@render_to("sim/player_index.html")
def __player_index(request):
    groups = SectionGroup.objects.filter(sectiongroupplayer__user=request.user)
    return dict(user=request.user, groups=groups)


def tab_name(i):
    if i < 4:
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
                 ) for i in range(1, 5)]

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
    if working_state.turn == 4:
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
        country_condition=working_state.statevariable_set.get(
            name='Country Condition').value,
        conditions=__current_conditions(working_state),
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
    roles = ('president', 'regional', 'envoy', 'opposition')
    # NOTE: we currently assume 4 turns indexed at 1
    for turn in range(1, 5):
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


def __current_conditions(state):
    details = {
        'Violence Level': {
            'most': 'non-violent',
            'least': 'genocide',
            'good_inverse': True
        },
        'Economy': {
            'least': 'depression',
            'most': 'stable',
            'good_inverse': True
        },
        'Prestige': {
            'least': 'globally isolated',
            'most': 'respected world player',
            'good_inverse': True
        },
        'Awareness': {
            'least': 'zero media coverage',
            'most': 'regular media coverage',
            'good_inverse': True
        },
        'Political Discourse': {
            'least': 'state control of information',
            'most': 'free and open system',
            'good_inverse': True
        },
        'Weapons Flow': {
            'most': 'minimal/no weapons smuggling',
            'least': 'uncontrolled weapons smuggling',
            'good_inverse': True
        },
    }
    conditions = []
    for k, var_dict in details.items():
        var = state.statevariable_set.get(name=k)
        var_dict['name'] = var.name
        var_dict['value'] = int(var.value)
        conditions.append(var_dict)
    return conditions


class FeedbackForm(forms.Form):
    feedback = forms.CharField(widget=forms.Textarea)
    faculty_id = forms.IntegerField(widget=forms.HiddenInput)
    turn_id = forms.IntegerField(widget=forms.HiddenInput)


def check_statechange(s, p, e, r, o, c, missing, duplicates):
    c = StateChange.objects.filter(
        state=s, president=p, envoy=e, regional=r, opposition=o).count()
    if c == 0:
        missing.append(
            dict(state=s, president=p, envoy=e, opposition=o, regional=r))
    if c > 1:
        duplicates.append(
            dict(state=s, president=p, envoy=e, opposition=o, regional=r))
    return (missing, duplicates)


@login_required
def check_statechanges(request):
    missing = []
    duplicates = []
    for s in State.objects.all():
        if s.turn == 4:
            continue  # no transitions out of the last state
        for p in [1, 2, 3]:
            for e in [1, 2, 3]:
                for r in [1, 2, 3]:
                    for o in [1, 2, 3]:
                        (missing, duplicates) = check_statechange(
                            s, p, e, r, o, missing, duplicates)
    return render(
        request,
        "sim/check_statechanges.html",
        dict(
            missing=missing,
            duplicates=duplicates,
            user=request.user,
        ))
