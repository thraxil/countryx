from django.test import TestCase
from .factories import SectionTurnDatesFactory
from countryx.sim.middleware import ensure_consistency_of_all_sections


class MiddlewareTest(TestCase):
    def test_no_sections(self):
        ensure_consistency_of_all_sections()

    def test_with_one_section(TestCase):
        SectionTurnDatesFactory()
        ensure_consistency_of_all_sections()
