from django.core.exceptions import PermissionDenied

from post.models import Post


def post_owner(f):
    def wrap(request, *args, **kwargs):
        post = Post.objects.get(pk=kwargs['post_pk'])
        if request.user == post.author:
            return f(request, *args, **kwargs)
        raise PermissionDenied
    return wrap
