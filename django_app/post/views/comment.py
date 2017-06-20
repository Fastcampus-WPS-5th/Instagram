from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from ..forms import CommentForm
from ..models import Post

__all__ = (
    'comment_create',
    'comment_modify',
    'comment_delete',
)


@require_POST
@login_required
def comment_create(request, post_pk):
    # POST요청을 받아 Comment객체를 생성 후 post_detail페이지로 redirect
    # CommentForm을 만들어서 해당 ModelForm안에서 생성/수정가능하도록 사용
    post = get_object_or_404(Post, pk=post_pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect('post:post_detail', post_pk=post.pk)


def comment_modify(request, post_pk):
    # 수정
    # CommentForm을 만들어서 해당 ModelForm안에서 생성/수정가능하도록 사용
    pass


def comment_delete(request, post_pk, comment_pk):
    # POST요청을 받아 Comment객체를 delete, 이후 post_detail페이지로 redirect
    pass
