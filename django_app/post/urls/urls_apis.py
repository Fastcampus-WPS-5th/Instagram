from django.conf.urls import url

from .. import apis

urlpatterns = [
    url(r'^$', apis.PostListCreateView.as_view()),
]
