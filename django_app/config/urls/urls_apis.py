from django.conf.urls import url, include

urlpatterns = [
    url(r'^post/', include('post.urls.urls_apis')),
    url(r'^member/', include('member.urls.urls_apis')),
]
