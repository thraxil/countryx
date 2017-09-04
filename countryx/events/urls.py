from django.conf.urls import url

import views

urlpatterns = [
    url(r'^$', views.ListEvents.as_view(), name='events-list'),
    url(r'^event/(?P<pk>\d+)/$', views.EventDetail.as_view(),
        name='event-detail'),
    url(r'^filter/$', views.FieldValueFilter.as_view(),
        name='field-value-filter'),
]
