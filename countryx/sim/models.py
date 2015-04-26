from django.db import models, connection
from django.contrib.auth.models import User
import datetime
import random
import re


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
        p = re.compile("[A-Z][a-z]*")
        return " ".join(p.findall(self.name))


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

    def __unicode__(self):
        return "Turn %s: %s" % (self.turn, self.name)

    def _countedges(self, myfield, otherfield, extra=''):
        tablename = StateChange._meta.db_table
        cursor = connection.cursor()
        cursor.execute(
            'SELECT "%s", count("%s") FROM "%s" WHERE "%s"=%d %s GROUP BY "%s"'
            % (otherfield, otherfield, tablename, myfield, self.id, extra,
               otherfield))
        return cursor.rowcount

    def influence_from(self, role):
        tablename = StateChange._meta.db_table
        myfield = StateChange._meta.get_field('next_state').column
        otherfield = StateChange._meta.get_field('state').column
        cursor = connection.cursor()
        cursor.execute(
            'SELECT "%s", count("%s") FROM "%s" WHERE "%s"=%d %s GROUP BY "%s"'
            % (otherfield, otherfield, tablename, myfield, self.id, '',
               otherfield))
        rv = []
        for row in cursor.fetchall():
            cursor.execute(
                'SELECT count("%s") FROM "%s" WHERE "%s"=%d AND '
                '"%s"=%d GROUP BY "%s"' % (
                    role, tablename, myfield, self.id, otherfield, row[0],
                    role))
            rv.append(3 - cursor.rowcount)
        return rv

    def get_color(self):
        colors = [
            'ffd478', '009192', 'ff9400', 'd25700', '935200', 'd4fb79',
            '73fa79', '8efa00', '4e8f00', '0096ff', '0a31ff', 'd783ff',
            '7a80ff', '531a93', 'ff8ad8', 'ff3092', 'ff40ff', '009051',
            '942092', '941751', '941200', 'ff2700', '005393', 'ff7e79',
            'fffc00', '76d6ff', '00f900', '929292', '929000']
        # when reimported ids get higher than 28.
        # The 28 should NOT be hard-coded
        key = (self.id % 28) + 1
        if len(colors) > key:
            return colors[key]
        else:
            # 255*255*255/28 states == 592191
            return str(hex(592191 * key))[2:]

    def full_to(self, roles):
        return [{'color': x.next_state.get_color(), 'ids': [x.next_state.id]}
                for x in StateChange.objects.filter(
                state=self).order_by(*roles)]

    def full_from(self, roles):
        default_color = 'FFFFFF'
        # don't do dictionaries here, since then they'll all be a
        # pointer to the same object
        rv = [False] * (3 ** len(roles))
        for ch in StateChange.objects.filter(next_state=self).order_by(*roles):
            index = sum([(3 ** (len(roles) - i - 1)) * (getattr(ch, r) - 1)
                         for i, r in enumerate(roles)])
            if not rv[index]:
                rv[index] = {'color': default_color, 'ids': []}

            rv[index]['ids'].append(ch.state.id)
            if rv[index]['color'] != default_color:
                rv[index]['color'] = '000000'
            else:
                rv[index]['color'] = ch.state.get_color()
        return rv

    def to_count(self, extra=''):
        return self._countedges(
            StateChange._meta.get_field('state').column,
            StateChange._meta.get_field('next_state').column,
            extra
        )

    def from_count(self, extra=''):
        return self._countedges(
            StateChange._meta.get_field('next_state').column,
            StateChange._meta.get_field('state').column,
            extra
        )

    def influence(self, role, func, count):
        rv = []
        for choice in range(1, 4):
            rv.append(count - func('AND %s=%d' % (role, choice)))
        return rv

    def edge_metadata(self):
        metadata = {
            'to': self.to_count(),
            'from': self.from_count(),
            'influence_from': {},
            'influence_to': {}}
        for role in ('president', 'envoy', 'regional', 'opposition'):
            metadata['influence_from'][role] = self.influence_from(role)
            metadata['influence_to'][role] = self.influence(
                role, self.to_count, metadata['to'])
        return metadata


class StateChange(models.Model):
    state = models.ForeignKey(State, related_name="%(class)s_related_current")
    president = models.IntegerField()
    envoy = models.IntegerField()
    regional = models.IntegerField()
    opposition = models.IntegerField()
    next_state = models.ForeignKey(State,
                                   related_name="%(class)s_related_next")

    def __unicode__(self):
        return "[%s] P=%s E%s R=%s O=%s >> [%s]" % (
            self.state, self.president, self.envoy, self.regional,
            self.opposition, self.next_state)


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

    def __unicode__(self):
        return "[%s] %s: %s. %s" % (self.state, self.role,
                                    self.choice, self.desc)

###############################################################################
###############################################################################


class Section(models.Model):
    name = models.CharField(max_length=20)
    term = models.CharField(max_length=20)
    year = models.IntegerField()
    created_date = models.DateTimeField('created_date')

    def __unicode__(self):
        return "%s %s %s" % (self.name, self.term, self.year)

    def current_turn(self):
        turn_dates = SectionTurnDates.objects.get(section=self)
        if (turn_dates.turn1 > datetime.datetime.now()):
            return 1
        elif (turn_dates.turn2 is None or
              turn_dates.turn2 > datetime.datetime.now()):
            return 2
        elif (turn_dates.turn3 is None or
              turn_dates.turn3 > datetime.datetime.now()):
            return 3
        return 4

    def current_turn_close_date(self):
        turn_dates = SectionTurnDates.objects.get(section=self)
        if (turn_dates.turn1 > datetime.datetime.now()):
            return turn_dates.turn1
        elif (turn_dates.turn2 is None or
              turn_dates.turn2 > datetime.datetime.now()):
            return turn_dates.turn2
        elif (turn_dates.turn3 is None or
              turn_dates.turn3 > datetime.datetime.now()):
            return turn_dates.turn3

        return turn_dates.turn1

    def end_turn(self):
        ct = self.current_turn()
        std = self.sectionturndates_set.all()[0]
        if ct == 1:
            std.turn1 = datetime.datetime.now()
        elif ct == 2:
            std.turn2 = datetime.datetime.now()
        elif ct == 3:
            std.turn3 = datetime.datetime.now()
        else:
            raise "This shouldn't have happened"
        std.save()

    def get_absolute_url(self):
        return "/sim/faculty/manage/%d/" % self.id

    def set_sectionturndates_to_default(self):
        """ sets turn dates on this section to one day apart starting now """
        dates = (datetime.datetime.now() + datetime.timedelta(hours=24),
                 datetime.datetime.now() + datetime.timedelta(hours=48),
                 datetime.datetime.now() + datetime.timedelta(hours=72))
        if self.sectionturndates_set.all().count() > 0:
            std = self.sectionturndates_set.all()[0]
            std.turn1 = dates[0]
            std.turn2 = dates[1]
            std.turn3 = dates[2]
            std.save()
            return std
        else:
            std = SectionTurnDates.objects.create(section=self,
                                                  turn1=dates[0],
                                                  turn2=dates[1],
                                                  turn3=dates[2],
                                                  )
            return std

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
        self.set_sectionturndates_to_default()
        start_state = State.objects.get(turn=1, state_no=1)

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


class SectionTurnDates(models.Model):
    section = models.ForeignKey(Section)
    turn1 = models.DateTimeField('turn1')
    turn2 = models.DateTimeField('turn2', null=True)
    turn3 = models.DateTimeField('turn3', null=True)

    def __unicode__(self):
        return "%s %s %s" % (self.turn1, self.turn2, self.turn3)


def get_or_create_section(name):
    """ fetches an existing section with a given name

    or creates a new one if necessary

    mostly used for the cheat functionality """
    try:
        return Section.objects.get(name=name)
    except Section.DoesNotExist:
        # need to make one
        return Section.objects.create(name=name, term="cheat", year=2009,
                                      created_date=datetime.datetime.now())


def get_or_create_user(username, first_name, last_name, email,
                       password, is_staff=False, is_superuser=False):
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return User.objects.create(username=username, first_name=first_name,
                                   last_name=last_name, email=email,
                                   password=password, is_staff=is_staff,
                                   is_superuser=is_superuser)

###############################################################################
###############################################################################

GROUP_PLAYER_COUNT = 4

GROUP_STATUS_NOACTION = 1
GROUP_STATUS_PENDING = 2
GROUP_STATUS_SUBMITTED = 4


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
            except:
                # player has no choice saved
                player_response = SectionGroupPlayerTurn.objects.create(
                    player=player, turn=state.turn)
                player_response.choice = random.randint(1, 3)
                player_response.submit_date = datetime.datetime.now()
                player_response.automatic_update = AUTOMATIC_UPDATE_RANDOM
                player_response.save()

    def update_state(self):
        state = self.sectiongroupstate_set.latest().state
        try:
            president = SectionGroupPlayerTurn.objects.get(
                player__role__name='President',
                player__group=self,
                turn=state.turn, submit_date__isnull=False)
            regional = SectionGroupPlayerTurn.objects.get(
                player__role__name='SubRegionalRep',
                player__group=self,
                turn=state.turn, submit_date__isnull=False)
            opposition = SectionGroupPlayerTurn.objects.get(
                player__role__name='OppositionLeadership',
                player__group=self, turn=state.turn,
                submit_date__isnull=False)
            envoy = SectionGroupPlayerTurn.objects.get(
                player__role__name='FirstWorldEnvoy',
                player__group=self,
                turn=state.turn, submit_date__isnull=False)
            next_state = StateChange.objects.get(
                state=state, president=president.choice,
                envoy=envoy.choice,
                regional=regional.choice,
                opposition=opposition.choice).next_state
            SectionGroupState.objects.create(
                state=next_state,
                group=self,
                date_updated=datetime.datetime.now())
        except:
            pass  # something is wrong with the group.

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
        if (self.state.turn == 4):
            return GROUP_STATUS_SUBMITTED
        status = 0
        players = self.group.sectiongroupplayer_set.all()
        for player in players:
            status += player.status(self.state)
        if (status == PLAYER_STATUS_NOACTION * GROUP_PLAYER_COUNT):
            return GROUP_STATUS_NOACTION
        elif (status == PLAYER_STATUS_SUBMITTED * GROUP_PLAYER_COUNT):
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


def ensure_consistency_of_all_sections():
    for section in Section.objects.all():
        section.ensure_consistency()
