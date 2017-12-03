from django.db import models


class Event(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, db_index=True)

    full_data = models.TextField(blank=True, default=u"")


class EventField(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, db_index=True)
    value = models.TextField(blank=True, default=u"")
