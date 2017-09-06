from django.test import TestCase
from datetime import datetime
from countryx.sim.models import (
    SectionAdministrator, compare_dicts)
from .factories import (
    RoleFactory, StateFactory, StateChangeFactory,
    StateVariableFactory, StateRoleChoiceFactory,
    SectionGroupFactory, SectionFactory,
    UserFactory, SectionGroupPlayerFactory,
    SectionGroupStateFactory, SectionGroupPlayerTurnFactory,
)


class RoleTest(TestCase):
    def test_unicode(self):
        r = RoleFactory()
        self.assertEqual(str(r), r.name)

    def test_display_name(self):
        r = RoleFactory()
        self.assertEqual(r.display_name(), 'role')


class StateTest(TestCase):
    def test_unicode(self):
        s = StateFactory()
        self.assertTrue(s.name in str(s))

    def test_get_color(self):
        s = StateFactory()
        self.assertEqual(len(s.get_color()), 6)

    def test_full_to(self):
        s = StateFactory()
        self.assertEqual(s.full_to([]), [])

    def test_full_from_empty(self):
        s = StateFactory()
        self.assertEqual(s.full_from([]), [False])

    def test_full_from(self):
        sc = StateChangeFactory()
        s = sc.next_state
        self.assertEqual(len(s.full_from([])), 1)

    def test_long_name(self):
        sc = StateFactory(name='123456789012345678901234567890')
        self.assertEqual(len(sc.name), 30)


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
        s = SectionFactory()
        self.assertEqual(s.current_turn(), 1)

    def test_end_turn(self):
        s = SectionFactory()
        s.end_turn()

    def test_clear_all_empty(self):
        s = SectionFactory()
        s.clear_all()

    def test_reset(self):
        s = SectionFactory()
        StateFactory(turn=1, state_no=1)
        s.reset()

    def test_ensure_consistency_empty(self):
        s = SectionFactory()
        s.ensure_consistency()

    def test_get_absolute_url(self):
        s = SectionFactory()
        self.assertTrue(s.get_absolute_url().startswith("/sim/faculty/"))

    def test_remove_faculty_already_not(self):
        s = SectionFactory()
        u = UserFactory()
        s.remove_faculty(u)

    def test_clear_all(self):
        sg = SectionGroupFactory()
        sg.section.clear_all()

    def test_add_faculty(self):
        s = SectionFactory()
        u = UserFactory()
        s.add_faculty(u)
        self.assertEqual(SectionAdministrator.objects.count(), 1)

        # no double add
        s.add_faculty(u)
        self.assertEqual(SectionAdministrator.objects.count(), 1)

    def test_remove_faculty(self):
        s = SectionFactory()
        u = UserFactory()
        s.add_faculty(u)
        self.assertEqual(SectionAdministrator.objects.count(), 1)
        s.remove_faculty(u)
        self.assertEqual(SectionAdministrator.objects.count(), 0)

    def test_ensure_consistency(self):
        s = SectionGroupFactory()
        StateFactory(turn=1, state_no=1)
        s.section.ensure_consistency()

    def test_long_name(self):
        s = SectionFactory(name='123456789012345678901234567890')
        self.assertEqual(len(s.name), 30)


class TestSectionGroup(TestCase):
    def test_unicode(self):
        sg = SectionGroupFactory()
        self.assertTrue(sg.name in str(sg))

    def test_make_state_current(self):
        sg = SectionGroupFactory()
        StateFactory(state_no=1, turn=1)
        sg.make_state_current(1)
        self.assertEqual(sg.sectiongroupstate_set.count(), 1)

    def test_role_choices(self):
        sgpt = SectionGroupPlayerTurnFactory(submit_date=datetime.now())
        group = sgpt.player.group
        self.assertEqual(
            group.role_choices(turn=sgpt.turn),
            {sgpt.player.role.name: sgpt.choice})

    def test_update_state_empty(self):
        sg = SectionGroupStateFactory().group
        sg.update_state()

    def test_udpate_state_with_roles(self):
        sgpt = SectionGroupPlayerTurnFactory()
        group = sgpt.player.group
        SectionGroupStateFactory(group=group)
        StateChangeFactory(state=group.current_state())
        group.update_state()

    def test_force_response_all_players(self):
        sg = SectionGroupStateFactory().group
        SectionGroupPlayerFactory(group=sg)
        sg.force_response_all_players()


class TestSectionGroupPlayer(TestCase):
    def test_unicode(self):
        p = SectionGroupPlayerFactory()
        self.assertTrue(":" in str(p))

    def test_current_status(self):
        p = SectionGroupPlayerFactory()
        SectionGroupStateFactory(group=p.group)
        self.assertEqual(p.current_status(), 1)


class TestSectionGroupState(TestCase):
    def test_status(self):
        sg = SectionGroupStateFactory()
        StateFactory(turn=4)
        self.assertEqual(sg.status(), 1)

    def test_status_end(self):
        sg = SectionGroupStateFactory()
        sg.state.turn = 4
        sg.state.save()
        self.assertEqual(sg.status(), 4)


class TestCompareDicts(TestCase):
    def test_same(self):
        a = {1: 2, 3: 4}
        b = {3: 4, 1: 2}
        self.assertTrue(compare_dicts(a, b))

    def test_different(self):
        a = {1: 2, 3: 4}
        b = {1: 1, 3: 4}
        self.assertFalse(compare_dicts(a, b))
