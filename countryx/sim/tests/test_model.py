from django.test import TestCase
from countryx.sim.models import Section, SectionGroup
from countryx.sim.models import SectionGroupPlayer
from countryx.sim.models import SectionGroupPlayerTurn
from countryx.sim.models import GROUP_STATUS_NOACTION, PLAYER_STATUS_NOACTION
from countryx.sim.models import PLAYER_STATUS_SUBMITTED, PLAYER_STATUS_PENDING
from countryx.sim.models import GROUP_STATUS_PENDING, GROUP_STATUS_SUBMITTED
from countryx.sim.models import State, SectionTurnDates
from countryx.sim.models import AUTOMATIC_UPDATE_FROMDRAFT
from countryx.sim.models import AUTOMATIC_UPDATE_NONE
from countryx.sim.models import AUTOMATIC_UPDATE_RANDOM
from .factories import (
    RoleFactory, StateFactory, StateChangeFactory,
    StateVariableFactory, StateRoleChoiceFactory,
    SectionTurnDatesFactory, SectionGroupFactory,
)
import datetime
import time


class RoleTest(TestCase):
    def test_unicode(self):
        r = RoleFactory()
        self.assertEqual(str(r), r.name)


class StateTest(TestCase):
    def test_unicode(self):
        s = StateFactory()
        self.assertTrue(s.name in str(s))

    def test_influence_from(self):
        s = StateFactory()
        self.assertEqual(s.influence_from(None), [])

    def test_get_color(self):
        s = StateFactory()
        self.assertEqual(s.get_color(), 'ff9400')

    def test_full_to(self):
        s = StateFactory()
        self.assertEqual(s.full_to([]), [])

    def test_full_from(self):
        s = StateFactory()
        self.assertEqual(s.full_from([]), [False])

    def test_to_count(self):
        s = StateFactory()
        self.assertEqual(s.to_count(), -1)

    def test_from_count(self):
        s = StateFactory()
        self.assertEqual(s.from_count(), -1)

    def test_edge_metadata(self):
        s = StateFactory()
        r = s.edge_metadata()
        self.assertTrue('from' in r)
        self.assertTrue('influence_from' in r)
        self.assertTrue('influence_to' in r)
        self.assertTrue('to' in r)


class TestStateChange(TestCase):
    def test_unicode(self):
        s = StateChangeFactory()
        r = str(s)
        self.assertTrue("[Turn " in r)
        self.assertTrue("state " in r)
        self.assertTrue("P=" in r)


class TestStateVariable(TestCase):
    def test_unicode(self):
        s = StateVariableFactory()
        r = str(s)
        self.assertTrue("[Turn " in r)
        self.assertTrue("state " in r)


class TestStateRoleChoice(TestCase):
    def test_unicode(self):
        s = StateRoleChoiceFactory()
        r = str(s)
        self.assertTrue("[Turn " in r)
        self.assertTrue("role " in r)


class TestSection(TestCase):
    def test_current_turn(self):
        std = SectionTurnDatesFactory()
        s = std.section
        self.assertEqual(s.current_turn(), 2)

    def test_current_turn_close_date(self):
        std = SectionTurnDatesFactory()
        s = std.section
        self.assertEqual(s.current_turn_close_date(), None)

    def test_end_turn(self):
        std = SectionTurnDatesFactory()
        s = std.section
        s.end_turn()

    def test_clear_all(self):
        std = SectionTurnDatesFactory()
        s = std.section
        s.clear_all()


class TestSectionGroup(TestCase):
    def test_unicode(self):
        sg = SectionGroupFactory()
        self.assertTrue(sg.name in str(sg))

    def test_make_state_current(self):
        sg = SectionGroupFactory()
        StateFactory(state_no=1, turn=1)
        sg.make_state_current(1)
        self.assertEqual(sg.sectiongroupstate_set.count(), 1)


class ModelTestCases(TestCase):
    fixtures = ["test_data.json"]

    def test_group_status_noaction(self):
        # update the data manually to setup this test
        group = SectionGroup.objects.get(
            name='A', section=Section.objects.get(name='Test'))
        self.assertEquals(GROUP_STATUS_NOACTION, group.status())

    def test_group_status_pending_submitted(self):
        # update the data manually to setup this test
        group = SectionGroup.objects.get(
            name='A', section=Section.objects.get(name='Test'))
        current_state = group.sectiongroupstate_set.latest().state
        players = SectionGroupPlayer.objects.filter(group=group)

        count = 0
        for player in players:
            SectionGroupPlayerTurn.objects.create(
                player=player, turn=current_state.turn, choice=1,
                submit_date=datetime.datetime.now(), reasoning="foobar")
            if count < 3:
                self.assertEquals(GROUP_STATUS_PENDING, group.status())
            else:
                self.assertEquals(GROUP_STATUS_SUBMITTED, group.status())
            count += 1

    def test_player_status(self):
        group = SectionGroup.objects.get(
            name='B', section=Section.objects.get(name='Test'))
        player = SectionGroupPlayer.objects.get(
            user__username='playerE', group=group)

        states = group.sectiongroupstate_set.all().order_by('state__turn')

        self.assertEquals(PLAYER_STATUS_NOACTION,
                          player.status(states[0].state))

        # create a draft for states[1]
        turn = SectionGroupPlayerTurn.objects.create(
            player=player, turn=states[0].state.turn,
            choice=1, reasoning="foobar")
        self.assertEquals(PLAYER_STATUS_PENDING,
                          player.status(states[0].state))

        turn.submit_date = datetime.datetime.now()
        turn.save()
        self.assertEquals(PLAYER_STATUS_SUBMITTED,
                          player.status(states[0].state))

    def test_player_current_status(self):
        group = SectionGroup.objects.get(
            name='B', section=Section.objects.get(name='Test'))
        player = SectionGroupPlayer.objects.get(
            user__username='playerE', group=group)

        self.assertEquals(PLAYER_STATUS_NOACTION, player.current_status())

    def test_section_current_turn(self):
        time_format = "%Y-%m-%d %H:%M"

        section = Section.objects.get(name="Test")
        turn_dates = SectionTurnDates.objects.get(section=section)
        turn_dates.turn1 = (datetime.datetime.now() +
                            datetime.timedelta(hours=1))
        turn_dates.save()

        self.assertEquals(1, section.current_turn())

        # make turn 1 be in the past & retest
        turn_dates = SectionTurnDates.objects.get(section=section)
        turn_dates.turn1 = datetime.datetime.fromtimestamp(
            time.mktime(time.strptime("2008-12-20 12:00", time_format)))
        turn_dates.turn2 = datetime.datetime.fromtimestamp(
            time.mktime(time.strptime("2020-01-20 12:00", time_format)))
        turn_dates.save()

        self.assertEquals(2, section.current_turn())

    def test_sectiongroup_force_response_all_players(self):
        # Group A has no player turns in the test data

        # Setup some helpful turns for Group A to test all the conditions
        group = SectionGroup.objects.get(
            name='A', section=Section.objects.get(name='Test'))
        state = group.sectiongroupstate_set.latest().state
        playerA = SectionGroupPlayer.objects.get(
            user__username='playerA', group=group)
        playerB = SectionGroupPlayer.objects.get(
            user__username='playerB', group=group)
        playerC = SectionGroupPlayer.objects.get(
            user__username='playerC', group=group)
        playerD = SectionGroupPlayer.objects.get(
            user__username='playerD', group=group)

        # create a draft for playerA
        SectionGroupPlayerTurn.objects.create(
            player=playerA, turn=state.turn, choice=1, reasoning="draft")

        # create a full submit for playerB
        SectionGroupPlayerTurn.objects.create(
            player=playerB, turn=state.turn, choice=2,
            reasoning="final", submit_date=datetime.datetime.now())

        # leave the other two players alone (playerC & payerD)
        group.force_response_all_players()

        a_turn = SectionGroupPlayerTurn.objects.get(
            player=playerA, turn=1, submit_date__isnull=False)
        self.assertEquals(1, a_turn.choice)
        self.assertEquals(AUTOMATIC_UPDATE_FROMDRAFT, a_turn.automatic_update)

        b_turn = SectionGroupPlayerTurn.objects.get(
            player=playerB, turn=1, submit_date__isnull=False)
        self.assertEquals(2, b_turn.choice)
        self.assertEquals(AUTOMATIC_UPDATE_NONE, b_turn.automatic_update)

        c_turn = SectionGroupPlayerTurn.objects.get(
            player=playerC, turn=1, submit_date__isnull=False)
        self.assert_(c_turn.choice > 0 and c_turn.choice < 4)
        self.assertEquals(AUTOMATIC_UPDATE_RANDOM, c_turn.automatic_update)

        d_turn = SectionGroupPlayerTurn.objects.get(
            player=playerD, turn=1, submit_date__isnull=False)
        self.assert_(d_turn.choice > 0 and d_turn.choice < 4)
        self.assertEquals(AUTOMATIC_UPDATE_RANDOM, d_turn.automatic_update)

    def test_sectiongroup_updatestate(self):
        # Group A has no player turns in the test data
        group = SectionGroup.objects.get(
            name='A', section=Section.objects.get(name='Test'))
        state = group.sectiongroupstate_set.latest().state

        group.update_state()

        # pick the responses for each player so we can verify the state choice
        players = SectionGroupPlayer.objects.filter(group=group)
        for player in players:
            SectionGroupPlayerTurn.objects.create(
                player=player, turn=state.turn, choice=2,
                reasoning="final", submit_date=datetime.datetime.now())

        # now, try to update the state
        group.update_state()
        state = group.sectiongroupstate_set.latest().state
        self.assertEquals(State.objects.get(turn=2, name="Violence - COIN"),
                          state)
        self.assertEquals(group.section.current_turn(), 2)

    def test_section_reset(self):
        # use another test to setup an in progress game
        self.test_sectiongroup_updatestate()

        section = Section.objects.get(name="Test")
        self.assertEquals(section.current_turn(), 2)

        section.reset()

        # at turn #1, not turn #2
        self.assertEquals(section.current_turn(), 1)

        dates = (datetime.datetime.now() + datetime.timedelta(hours=24),
                 datetime.datetime.now() + datetime.timedelta(hours=48),
                 datetime.datetime.now() + datetime.timedelta(hours=72))

        # turn dates reset
        turn_dates = SectionTurnDates.objects.get(section=section)
        self.assertEquals(turn_dates.turn1.strftime('%m%d%Y'),
                          dates[0].strftime('%m%d%Y'))
        self.assertEquals(turn_dates.turn2.strftime('%m%d%Y'),
                          dates[1].strftime('%m%d%Y'))
        self.assertEquals(turn_dates.turn3.strftime('%m%d%Y'),
                          dates[2].strftime('%m%d%Y'))

        for group in section.sectiongroup_set.all():
            self.assertEquals(group.status(), GROUP_STATUS_NOACTION)
            state = group.sectiongroupstate_set.latest().state
            self.assertEquals(State.objects.get(turn=1, name="Start"), state)
            self.assertEquals(group.section.current_turn(), 1)

            players = SectionGroupPlayer.objects.filter(group=group)
            for player in players:
                player_response = SectionGroupPlayerTurn.objects.filter(
                    player=player)
                self.assertEquals(len(player_response), 0)
