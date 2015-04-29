from django.test import TestCase
from countryx.sim.models import ensure_consistency_of_all_sections
from .factories import (
    RoleFactory, StateFactory, StateChangeFactory,
    StateVariableFactory, StateRoleChoiceFactory,
    SectionGroupFactory, SectionFactory,
    UserFactory,
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

    def test_influence_from(self):
        s = StateFactory()
        self.assertEqual(s.influence_from(None), [])

    def test_get_color(self):
        s = StateFactory()
        self.assertEqual(len(s.get_color()), 6)

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
        s = SectionFactory()
        self.assertEqual(s.current_turn(), 1)

    def test_end_turn(self):
        s = SectionFactory()
        s.end_turn()

    def test_clear_all(self):
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


class TestSectionGroup(TestCase):
    def test_unicode(self):
        sg = SectionGroupFactory()
        self.assertTrue(sg.name in str(sg))

    def test_make_state_current(self):
        sg = SectionGroupFactory()
        StateFactory(state_no=1, turn=1)
        sg.make_state_current(1)
        self.assertEqual(sg.sectiongroupstate_set.count(), 1)


class ConsistencyEnforcementTest(TestCase):
    def test_no_sections(self):
        ensure_consistency_of_all_sections()

    def test_with_one_section(TestCase):
        SectionFactory()
        ensure_consistency_of_all_sections()
