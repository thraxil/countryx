from django.utils.encoding import force_text
from six import iteritems
import json


class EventService(object):
    def add(self, name, request=None, **fields):
        from .models import Event
        fields.update(self._process_request(request))
        event = Event.objects.create(name=name, full_data=json.dumps(fields))
        for k, v in iteritems(fields):
            self._add_field(event, k, v)
        self.event = event
        return self

    def _process_request(self, request=None):
        if request is None:
            return dict()

        fields = dict()
        fields['request_method'] = request.method
        fields['request_path'] = request.get_full_path()
        fields['request_remote_addr'] = request.META.get('REMOTE_ADDR')
        fields['request_user_agent'] = request.META.get('HTTP_USER_AGENT')
        fields['request_referer'] = request.META.get('HTTP_REFERER')

        if request.user.is_authenticated:
            fields['request_user'] = request.user.username
            fields['request_authenticated'] = True
        else:
            fields['request_user'] = 'anonymous'
            fields['request_authenticated'] = False
        return fields

    def _add_field(self, event, name, value):
        # ignore lists, dicts, etc.
        if isinstance(value, list) or isinstance(value, dict):
            return
        from .models import EventField
        # otherwise, stringify it and call it good
        value = force_text(value)
        EventField.objects.create(
            event=event,
            name=name,
            value=value,
        )
