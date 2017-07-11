from django.conf import settings
from django.db import models

from utils.fields import CustomImageField

__all__ = (
    'Post',
    'PostLike',
)


class Post(models.Model):
    # Django가 제공하는 기본 settings.AUTH_USER_MODEL와 연결되도록 수정
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

    class Meta:
        ordering = ['-pk', ]

    def add_comment(self, user, content):
        # 자신을 post로 갖고, 전달받은 user를 author로 가지며
        # content를 content필드내용으로 넣는 Comment객체 생성
        return self.comment_set.create(author=user, content=content)

    @property
    def like_count(self):
        # 자신을 like하고 있는 user수 리턴
        return self.like_users.count()

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
