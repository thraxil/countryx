from django.test import TestCase
from .factories import (
    RoleFactory, StateFactory, StateChangeFactory,
    StateVariableFactory, StateRoleChoiceFactory,
    SectionTurnDatesFactory, SectionGroupFactory,
)


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
