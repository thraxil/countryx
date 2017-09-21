from django.conf.urls import url

import views

urlpatterns = [
    url(r'^$', views.ReportIndex.as_view(), name='reports-index'),
    url(r'^user/$', views.UserList.as_view(), name='reports-user-list'),
    url(r'^user/(?P<username>\w+)/$', views.UserDetail.as_view(),
        name='reports-user-detail'),
]
