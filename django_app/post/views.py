from django.shortcuts import render
from .models import Post


def post_list(request):
    # 모든 Post목록을 'posts'라는 key로 context에 담아 return render처리
    # post/post_list.html을 template으로 사용하도록 한다

    # 각 포스트에 대해 최대 4개까지의 댓글을 보여주도록 템플릿에 설정
    posts = Post.objects.all()
    context = {
        'posts': posts,
    }
    return render(request, 'post/post_list.html', context)


def post_detail(request, post_pk):
    # post_pk에 해당하는 Post객체를 리턴, 보여줌
    pass


def post_create(request):
    # POST요청을 받아 Post객체를 생성 후 post_list페이지로 redirect
    pass


def post_modify(request, post_pk):
    # 수정
    pass


def post_delete(request, post_pk):
    # post_pk에 해당하는 Post에 대한 delete요청만을 받음
    # 처리완료후에는 post_list페이지로 redirect
    pass


def comment_create(request, post_pk):
    # POST요청을 받아 Comment객체를 생성 후 post_detail페이지로 redirect
    pass


def comment_modify(request, post_pk):
    # 수정
    pass


def comment_delete(request, post_pk, comment_pk):
    # POST요청을 받아 Comment객체를 delete, 이후 post_detail페이지로 redirect
    pass
