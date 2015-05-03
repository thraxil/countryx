from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse
import datetime
import json
import random

NUM_CHOICES = 3


class Role(models.Model):
    """
    A role allows a player to assume a specific persona in the game.
    Roles are associated with State Changes and Role Choices
    """
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField()

    def __unicode__(self):
        return self.name

    def display_name(self):
        parts = self.name.split(" ")
        return parts[0]

    def get_absolute_url(self):
        return reverse('role', args=(self.id,))


class State(models.Model):
    """
    A state represents a current country condition. Each state has a set of
    representative values (violence, esteem, etc), choices that each player
    role can follow and the list of states these choices can lead to.

    #Create a state
    >>> state = State.objects.create(name="Test", turn=1, state_no=1)
    >>> state
    <State: Turn 1: Test>
    """

    turn = models.IntegerField()
    state_no = models.IntegerField()
    name = models.CharField(max_length=40)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['turn', 'state_no']

    def __unicode__(self):
        return "Turn %s: %s" % (self.turn, self.name)

    def get_absolute_url(self):
        return reverse('state', args=(self.id,))

    def get_color(self):
        colors = settings.STATE_COLORS
        key = (self.id % len(colors))
        if len(colors) > key:
            return colors[key]
        else:
            # 255*255*255/28 states == 592191
            return str(hex(592191 * key))[2:]

    def to_states(self):
        return StateChange.objects.filter(state=self).order_by('next_state')

    def from_states(self):
        return StateChange.objects.filter(next_state=self).order_by('state')

    def full_to(self, roles):
        return [{'color': x.next_state.get_color(), 'ids': [x.next_state.id]}
                for x in StateChange.objects.filter(
                state=self).order_by(*roles)]

    def full_from(self, roles):
        default_color = 'FFFFFF'
        # don't do dictionaries here, since then they'll all be a
        # pointer to the same object
        rv = [False] * (NUM_CHOICES ** len(roles))
        for ch in StateChange.objects.filter(next_state=self).order_by(*roles):
            index = sum(
                [(NUM_CHOICES ** (len(roles) - i - 1)) * (getattr(ch, r) - 1)
                 for i, r in enumerate(roles)])
            if not rv[index]:
                rv[index] = {'color': default_color, 'ids': []}

            rv[index]['ids'].append(ch.state.id)
            if rv[index]['color'] != default_color:
                rv[index]['color'] = '000000'
            else:
                rv[index]['color'] = ch.state.get_color()
        return rv

    def country_condition(self):
        return self.statevariable_set.get(name='Country Condition').value


def num_turns():
    if State.objects.count() == 0:
        return 0
    return State.objects.all().aggregate(models.Max('turn'))['turn__max']


class StateChange(models.Model):
    state = models.ForeignKey(State, related_name="%(class)s_related_current")
    next_state = models.ForeignKey(State,
                                   related_name="%(class)s_related_next")
    # in here, we store some json. it will look something like:
    # {'President': 1, 'Envoy': 2, ...}
    # Role -> integer choice
    roles = models.TextField(blank=True)

    def __unicode__(self):
        rolesstr = " ".join(
            "%s=%d" % (k[0], v) for k, v in json.loads(self.roles).items()
        )
        return "[%s] %s >> [%s]" % (
            self.state, rolesstr, self.next_state)

    def show_choices(self):
        """ more useful format for displaying """
        j = json.loads(self.roles)
        choices = []
        for k in sorted(j.keys()):
            choices.append(dict(role=k, choice=j[k]))
        return choices


class StateVariable(models.Model):
    state = models.ForeignKey(State)
    name = models.CharField(max_length=20)
    value = models.TextField()

    def __unicode__(self):
        return "[%s] %s: %s" % (self.state, self.name, self.value)


class StateRoleChoice(models.Model):
    state = models.ForeignKey(State)
    role = models.ForeignKey(Role)
    choice = models.IntegerField()
    desc = models.CharField(max_length=250)

    class Meta:
        ordering = ['state', 'role', 'choice']

    def __unicode__(self):
        return "[%s] %s: %s. %s" % (self.state, self.role,
                                    self.choice, self.desc)

###############################################################################
###############################################################################


class Section(models.Model):
    name = models.CharField(max_length=20)
    created_date = models.DateTimeField('created_date')
    turn = models.IntegerField(default=1)

    def __unicode__(self):
        return self.name

    def current_turn(self):
        return self.turn

    def end_turn(self):
        self.turn = self.turn + 1
        self.save()

    def get_absolute_url(self):
        return "/sim/faculty/manage/%d/" % self.id

    def clear_all(self):
        """ clear out all the groups in the section
        (and their games by extension) """
        for g in self.sectiongroup_set.all():
            g.delete()

    def add_faculty(self, user):
        """ make sure that the user is set as faculty for this group """
        if self.sectionadministrator_set.filter(user=user).count() == 0:
            SectionAdministrator.objects.create(section=self, user=user)

    def remove_faculty(self, user):
        """ make sure the user isn't faculty for this section """
        try:
            sa = SectionAdministrator.objects.get(section=self, user=user)
            sa.delete()
        except SectionAdministrator.DoesNotExist:
            pass

    def reset(self):
        """ reset the section back to its Start state """
        self.turn = 1
        self.save()
        self.reset_sectiongroupstates()

    def reset_sectiongroupstates(self):
        start_state, _ = State.objects.get_or_create(turn=1, state_no=1)
        for g in self.sectiongroup_set.all():
            # Remove all state rows for this group
            g.sectiongroupstate_set.all().delete()

            players = SectionGroupPlayer.objects.filter(group=g)
            for player in players:
                # remove all player responses
                player_response = SectionGroupPlayerTurn.objects.filter(
                    player=player)
                player_response.delete()

            # put group in the start state automatically
            SectionGroupState.objects.create(
                group=g,
                state=start_state,
                date_updated=datetime.datetime.now())

    def ensure_consistency(self):
        section_turn = self.current_turn()
        # verify each group's current state == the current section turn
        # if not, then add the state to the group and make sure all
        # members get automated answers.
        groups = self.sectiongroup_set.all()
        for group in groups:
            group.make_state_current(section_turn)


class SectionAdministrator(models.Model):
    user = models.ForeignKey(User)
    section = models.ForeignKey(Section)

    def __unicode__(self):
        return "%s" % (self.user)


###############################################################################
###############################################################################

GROUP_STATUS_NOACTION = 1
GROUP_STATUS_PENDING = 2
GROUP_STATUS_SUBMITTED = 4


def compare_dicts(a, b):
    """ every k,v in a must have a match in b.
    the converse doesn't necessarily have to be true.
    ie, there can be a key in b that does not exist in a
    and it's still good enough"""
    for k, v in a.items():
        if b[k] != v:
            return False
    return True


class SectionGroup(models.Model):
    name = models.CharField(max_length=20)
    section = models.ForeignKey(Section)

    def __unicode__(self):
        return "%s: Group %s" % (self.section, self.name)

    def status(self):
        return self.sectiongroupstate_set.latest().status()

    def status_name(self):
        statuses = {GROUP_STATUS_NOACTION: "no action",
                    GROUP_STATUS_PENDING: "pending",
                    GROUP_STATUS_SUBMITTED: "submitted"}
        return statuses[self.status()]

    def force_response_all_players(self):
        random.seed(None)
        state = self.sectiongroupstate_set.latest().state
        players = SectionGroupPlayer.objects.filter(group=self)

        for player in players:
            # create or update the player's choice
            try:
                # check to see if player has a "draft" saved.
                # Use this if possible.
                player_response = SectionGroupPlayerTurn.objects.get(
                    player=player, turn=state.turn)
                if player_response.submit_date is None:
                    player_response.submit_date = datetime.datetime.now()
                    player_response.automatic_update =\
                        AUTOMATIC_UPDATE_FROMDRAFT
                    player_response.save()
            except SectionGroupPlayerTurn.DoesNotExist:
                # player has no choice saved
                player_response = SectionGroupPlayerTurn.objects.create(
                    player=player, turn=state.turn)
                player_response.choice = random.randint(1, NUM_CHOICES)
                player_response.submit_date = datetime.datetime.now()
                player_response.automatic_update = AUTOMATIC_UPDATE_RANDOM
                player_response.save()

    def current_state(self):
        return self.sectiongroupstate_set.latest().state

    def role_choices(self, turn=None):
        if turn is None:
            turn = self.current_state().turn
        choices = dict()
        sgpts = SectionGroupPlayerTurn.objects.filter(
            player__group=self,
            turn=turn,
            submit_date__isnull=False
        )
        for s in sgpts:
            choices[s.player.role.name] = s.choice
        return choices

    def update_state(self):
        choices = self.role_choices()
        for sc in StateChange.objects.filter(state=self.current_state()):
            roles = json.loads(sc.roles)
            if compare_dicts(choices, roles):
                next_state = sc.next_state
                SectionGroupState.objects.create(
                    state=next_state,
                    group=self,
                    date_updated=datetime.datetime.now())
                # and we're done
                return

    def make_state_current(self, section_turn):
        try:
            group_state = self.sectiongroupstate_set.latest().state
        except SectionGroupState.DoesNotExist:
            group_state = State.objects.get(state_no=1, turn=1)
            SectionGroupState.objects.create(
                state=group_state, group=self,
                date_updated=datetime.datetime.now())
        if (section_turn != group_state.turn):
            self.force_response_all_players()
            # update the group state to the next turn based on
            # the player choices
            self.update_state()


class SectionGroupState(models.Model):
    state = models.ForeignKey(State)
    group = models.ForeignKey(SectionGroup)
    date_updated = models.DateTimeField('date updated')

    class Meta:
        get_latest_by = 'date_updated'

    def __unicode__(self):
        return "%s %s" % (self.state, self.date_updated)

    def status(self):
        if (self.state.turn == num_turns()):
            return GROUP_STATUS_SUBMITTED
        status = 0
        players = self.group.sectiongroupplayer_set.all()
        for player in players:
            status += player.status(self.state)
        if (status == PLAYER_STATUS_NOACTION * Role.objects.count()):
            return GROUP_STATUS_NOACTION
        elif (status == PLAYER_STATUS_SUBMITTED * Role.objects.count()):
            return GROUP_STATUS_SUBMITTED
        else:
            return GROUP_STATUS_PENDING

PLAYER_STATUS_NOACTION = 1
PLAYER_STATUS_PENDING = 2
PLAYER_STATUS_SUBMITTED = 4


class SectionGroupPlayer(models.Model):
    user = models.ForeignKey(User)
    group = models.ForeignKey(SectionGroup)
    role = models.ForeignKey(Role)

    def __unicode__(self):
        return "%s: [%s, %s]" % (self.user, self.role.name, self.group)

    def current_status(self):
        current_state = self.group.sectiongroupstate_set.latest().state
        return self.status(current_state)

    def status(self, current_state):
        action = PLAYER_STATUS_NOACTION

        if (self.sectiongroupplayerturn_related_player.all().count() > 0):
            try:
                turn = self.sectiongroupplayerturn_related_player.get(
                    turn=current_state.turn)
                if turn.submit_date:
                    action = PLAYER_STATUS_SUBMITTED
                else:
                    action = PLAYER_STATUS_PENDING
            except SectionGroupPlayerTurn.DoesNotExist:
                pass
        return action

AUTOMATIC_UPDATE_NONE = 0
AUTOMATIC_UPDATE_FROMDRAFT = 1
AUTOMATIC_UPDATE_RANDOM = 2


class SectionGroupPlayerTurn(models.Model):
    player = models.ForeignKey(SectionGroupPlayer,
                               related_name="%(class)s_related_player")
    turn = models.IntegerField()
    choice = models.IntegerField(null=True)
    reasoning = models.TextField(null=True)
    automatic_update = models.IntegerField(default=0)
    submit_date = models.DateTimeField('final date submitted', null=True)
    feedback = models.TextField(null=True)
    faculty = models.ForeignKey(SectionAdministrator,
                                related_name="%(class)s_related_faculty",
                                null=True)
    feedback_date = models.DateTimeField('feedback submitted', null=True)

    class Meta:
        get_latest_by = 'submit_date'

    def __unicode__(self):
        return "%s: Turn: %s Selected: %s" % (self.player,
                                              self.turn, self.choice)

    def is_submitted(self):
        return self.submit_date is not None
