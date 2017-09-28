from django.conf.urls import url

from .views import ReportIndex, UserList, UserDetail, GroupList, GroupDetail

urlpatterns = [
    url(r'^$', ReportIndex.as_view(), name='reports-index'),
    url(r'^user/$', UserList.as_view(), name='reports-user-list'),
    url(r'^user/(?P<username>\w+)/$', UserDetail.as_view(),
        name='reports-user-detail'),

    url(r'^group/$', GroupList.as_view(), name='reports-group-list'),
    url(r'^group/(?P<group_id>\d+)/$', GroupDetail.as_view(),
        name='reports-group-detail'),
]
