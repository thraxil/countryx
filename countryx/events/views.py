from django.views.generic import ListView

from .models import Event

from countryx.sim.views import StaffOnlyMixin


class ListEvents(StaffOnlyMixin, ListView):
    model = Event

    def get_queryset(self):
        return Event.objects.all().order_by('-timestamp')
