from django.shortcuts import render
from django.views.generic import ListView, DetailView, View

from .models import Event, EventField

from countryx.sim.views import StaffOnlyMixin


class ListEvents(StaffOnlyMixin, ListView):
    model = Event
    paginate_by = 200

    def get_queryset(self):
        return Event.objects.all().order_by('-timestamp')


class EventDetail(StaffOnlyMixin, DetailView):
    model = Event


class FieldValueFilter(StaffOnlyMixin, View):
    template_name = "events/field_value_filter.html"

    def get(self, request):
        field = request.GET.get('field')
        value = request.GET.get('value')
        fields = EventField.objects.filter(
            name=field, value=value
        ).order_by('-event__timestamp')[:200]
        return render(request, self.template_name,
                      dict(fields=fields, field=field, value=value))
