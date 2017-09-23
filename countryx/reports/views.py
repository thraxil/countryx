from django.contrib.auth.models import User
from django.views.generic import TemplateView

from countryx.events.models import EventField
from countryx.sim.models import Section, SectionGroup


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

    def user(self):
        return User.objects.get(username=self.event.eventfield_set.filter(
            name='request_user').first().value)


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


class GroupList(TemplateView):
    template_name = "reports/group_list.html"

    def get_context_data(self, **kwargs):
        context = super(GroupList, self).get_context_data(**kwargs)
        group_ids = set(ef.value for ef in EventField.objects.filter(
            name='group_id'))
        groups = set()
        for gid in group_ids:
            try:
                sg = SectionGroup.objects.get(id=gid)
                groups.add(sg)
            except SectionGroup.DoesNotExist:
                pass
        context['groups'] = sorted(groups, key=lambda x: x.name)
        return context


def remove_faculty_gets(events):
    for e in events:
        if e.user().is_staff and e.request_method() == "GET":
            continue
        yield e
    return


class GroupDetail(TemplateView):
    template_name = "reports/group_detail.html"

    def get_context_data(self, **kwargs):
        context = super(GroupDetail, self).get_context_data(**kwargs)
        group_id = kwargs['group_id']

        events = set([DisplayEvent(f.event) for f in EventField.objects.filter(
            name='group_id', value=group_id)])
        context['group_id'] = group_id
        context['group'] = SectionGroup.objects.get(id=group_id)

        section_events = set([DisplayEvent(f.event)
                              for f in EventField.objects.filter(
            name='section_id', value=context['group'].section.id
        )])
        events = events | section_events

        context['events'] = sorted(remove_faculty_gets(list(events)),
                                   key=lambda x: x.timestamp())
        return context
