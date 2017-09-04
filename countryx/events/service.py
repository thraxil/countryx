from .models import Event, EventField
import json


class EventService(object):
    def add(self, name, request=None, **fields):
        fields.update(self._process_request(request))
        event = Event.objects.create(name=name, full_data=json.dumps(fields))
        for k, v in fields.iteritems():
            self._add_field(event, k, v)

    def _process_request(self, request=None):
        if request is None:
            return dict()

        fields = dict()
        fields['request_method'] = request.METHOD
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

        # otherwise, stringify it and call it good
        value = unicode(value)
        EventField.objects.create(
            event=event,
            name=name,
            value=value,
        )
