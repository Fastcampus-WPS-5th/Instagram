from config.celery import app


@app.task
def task_update_post_like_count(post_pk):
    from post.models import Post
    post = Post.objects.get(pk=post_pk)
    post.calc_like_count()
    return post.like_count
