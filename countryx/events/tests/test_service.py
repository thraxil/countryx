from django.test import TestCase

from ..service import EventService
from ..models import Event, EventField


class EventServiceTest(TestCase):
    def test_add_basics(self):
        e = EventService()
        e.add('test1')

        self.assertEqual(Event.objects.filter(name='test1').count(), 1)
        self.assertEqual(EventField.objects.all().count(), 0)

        e.add('test2', field1='a string')
        self.assertEqual(Event.objects.filter(name='test2').count(), 1)
        self.assertEqual(EventField.objects.filter(
            name='field1', value='a string').count(), 1)
