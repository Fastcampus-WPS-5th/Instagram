import time
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from utils.fields import CustomImageField

__all__ = (
    'Post',
    'PostLike',
)


class Post(models.Model):
    # 1. 이 Post를 좋아요 한 개수를 저장할 수 있는 필드(like_count)를 생성 -> migration
    # 2. 이 Post에 연결된 PostLike의 개수를 가져와서 해당 필드에 저장하는 메서드 구현
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    photo = CustomImageField(upload_to='post', blank=True)
    video = models.ForeignKey('Video', blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    my_comment = models.OneToOneField(
        'Comment',
        blank=True,
        null=True,
        related_name='+'
    )
    like_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='like_posts',
        through='PostLike',
    )
    like_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-pk', ]

    def add_comment(self, user, content):
        # 자신을 post로 갖고, 전달받은 user를 author로 가지며
        # content를 content필드내용으로 넣는 Comment객체 생성
        return self.comment_set.create(author=user, content=content)

    # 이 메서드를 적절한 곳에서 호출
    def calc_like_count(self):
        time.sleep(6)
        self.like_count = self.like_users.count()
        self.save()

    @property
    def comments(self):
        """my_comment를 제외한 Comment역참조 쿼리셋"""
        if self.my_comment:
            return self.comment_set.exclude(pk=self.my_comment.pk)
        return self.comment_set.all()


class PostLike(models.Model):
    post = models.ForeignKey(Post)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            ('post', 'user'),
        )


@receiver(post_save, sender=PostLike)
@receiver(post_delete, sender=PostLike)
def update_post_like_count(sender, instance, **kwargs):
    print('Signal update_post_like_count, instance: {}'.format(
        instance
    ))
    instance.post.calc_like_count()
