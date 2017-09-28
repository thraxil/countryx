from django.conf.urls import url

from .views import ListEvents, EventDetail, FieldValueFilter

urlpatterns = [
    url(r'^$', ListEvents.as_view(), name='events-list'),
    url(r'^event/(?P<pk>\d+)/$', EventDetail.as_view(),
        name='event-detail'),
    url(r'^filter/$', FieldValueFilter.as_view(),
        name='field-value-filter'),
]
