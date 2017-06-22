from django.conf.urls import url
from . import views

# URL Namespace
# https://docs.djangoproject.com/en/1.11/topics/http/urls/#url-namespaces
app_name = 'post'
urlpatterns = [
    # url() 사용법
    # https://docs.djangoproject.com/en/1.11/ref/urls/#url

    # post_list와 매칭
    # /post/$
    url(r'^$', views.post_list, name='post_list'),

    # post_detail과 매칭
    # /post/3/$, /post/35/$
    # 정규표현식에서 매칭된 그룹을 위치인수로 반환하는 방법
    # url(r'^(\d+)/$', views.post_detail),

    # 정규표현식에서 매칭된 그룹을 키워드인수로 반환하는 방법
    # 그룹의 가장 앞 부분에 ?P<패턴이름>을 지정
    url(r'^(?P<post_pk>\d+)/$', views.post_detail, name='post_detail'),

    # post_create와 매칭
    url(r'^create/$', views.post_create, name='post_create'),

    # post_modify와 매칭
    url(r'^(?P<post_pk>\d+)/modify/$', views.post_modify, name='post_modify'),

    # post_delete와 매칭
    url(r'^(?P<post_pk>\d+)/delete/$', views.post_delete, name='post_delete'),

    # post_like와 매칭
    url(r'^(?P<post_pk>\d+)/like-toggle/$', views.post_like_toggle, name='post_like_toggle'),

    # comment_create와 매칭
    url(r'^(?P<post_pk>\d+)/comment/create/$', views.comment_create, name='comment_create'),

    # comment_modify와 매칭
    url(r'^comment/(?P<comment_pk>\d+)/modify/$', views.comment_modify, name='comment_modify'),

    # comment_delete와 매칭
    url(r'^comment/(?P<comment_pk>\d+)/delete/$', views.comment_delete, name='comment_delete'),

    # hashtag_post_list와 매칭
    url(r'^tag/(?P<tag_name>\w+)/$', views.hashtag_post_list, name='hashtag_post_list'),

    # 위쪽의 결과들과 매칭되지 않을 경우
    # url(r'^.*/$', views.post_anyway, name='post_anyway'),
]
