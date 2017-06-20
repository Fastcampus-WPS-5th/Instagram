from django.core.exceptions import PermissionDenied

from .models import Post, Comment


def post_owner(f):
    def wrap(request, *args, **kwargs):
        post = Post.objects.get(pk=kwargs['post_pk'])
        if request.user == post.author:
            return f(request, *args, **kwargs)
        raise PermissionDenied

    return wrap


def comment_owner(f):
    def wrap(request, *args, **kwargs):
        comment = Comment.objects.get(pk=kwargs['comment_pk'])
        if request.user == comment.author:
            return f(request, *args, **kwargs)
        raise PermissionDenied

    return wrap
