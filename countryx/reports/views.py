from django.views.generic import TemplateView

from countryx.events.models import EventField
from countryx.sim.models import Section


class ReportIndex(TemplateView):
    template_name = "reports/index.html"


class UserList(TemplateView):
    template_name = "reports/user_list.html"

    def get_context_data(self, **kwargs):
        context = super(UserList, self).get_context_data(**kwargs)
        users = set([ef.value for ef in EventField.objects.filter(
            name='request_user')])
        context['users'] = sorted(users)
        return context


class DisplayEvent(object):
    def __init__(self, event):
        self.event = event

    def name(self):
        return self.event.name

    def id(self):
        return self.event.id

    def timestamp(self):
        return self.event.timestamp

    def turn(self):
        qs = self.event.eventfield_set.filter(name='turn_id').first()
        if qs is not None:
            return qs.value
        else:
            return ""

    def request_method(self):
        return self.event.eventfield_set.filter(
            name='request_method').first().value

    def request_path(self):
        return self.event.eventfield_set.filter(
            name='request_path').first().value

    def reasoning(self):
        try:
            return self.event.eventfield_set.filter(
                name='reasoning').first().value
        except AttributeError:
            return None

    def choice(self):
        try:
            return self.event.eventfield_set.filter(
                name='choice_id').first().value
        except AttributeError:
            return None

    def section(self):
        try:
            section_id = self.event.eventfield_set.filter(
                name='section_id').first().value
            s = Section.objects.get(id=section_id)
            return s.name
        except AttributeError:
            return None


class UserDetail(TemplateView):
    template_name = "reports/user_detail.html"

    def get_context_data(self, **kwargs):
        context = super(UserDetail, self).get_context_data(**kwargs)
        username = kwargs['username']

        events = [DisplayEvent(f.event) for f in EventField.objects.filter(
            name='request_user', value=username)]
        context['events'] = sorted(events, key=lambda x: x.timestamp())
        context['username'] = username
        return context
