from django.conf.urls import url

from .. import apis

urlpatterns = [
    url(r'^(?P<pk>\d+)/$', apis.UserRetrieveUpdateDestroyView.as_view()),
]
