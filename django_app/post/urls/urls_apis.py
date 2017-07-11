from django.conf.urls import url

from .. import apis

urlpatterns = [
    url(r'^$', apis.PostListView.as_view()),
]
