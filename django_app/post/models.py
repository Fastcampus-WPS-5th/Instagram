"""
member application생성
    settings.AUTH_USER_MODEL모델 구현
        username, nickname
이후 해당 settings.AUTH_USER_MODEL모델을 Post나 Comment에서 author나 user항목으로 참조
"""
import re
from django.conf import settings
from django.db import models
from django.urls import reverse


class Post(models.Model):
    # Django가 제공하는 기본 settings.AUTH_USER_MODEL와 연결되도록 수정
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    photo = models.ImageField(upload_to='post', blank=True)
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


class PostLike(models.Model):
    post = models.ForeignKey(Post)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_date = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    post = models.ForeignKey(Post)
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    content = models.TextField()
    html_content = models.TextField(blank=True)
    tags = models.ManyToManyField('Tag')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    like_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='CommentLike',
        related_name='like_comments',
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.make_html_content_and_add_tags()

    def make_html_content_and_add_tags(self):
        # 해시태그에 해당하는 정규표현식
        p = re.compile(r'(#\w+)')
        # findall메서드로 해시태그 문자열들을 가져옴
        tag_name_list = re.findall(p, self.content)
        # 기존 content(Comment내용)을 변수에 할당
        ori_content = self.content
        # 문자열들을 순회하며
        for tag_name in tag_name_list:
            # Tag객체를 가져오거나 생성, 생성여부는 쓰지않는 변수이므로 _처리
            tag, _ = Tag.objects.get_or_create(name=tag_name.replace('#', ''))
            # 기존 content의 내용을 변경
            change_tag = '<a href="{url}" class="hash-tag">{tag_name}</a>'.format(
                # url=reverse('post:hashtag_post_list', args=[tag_name.replace('#', '')]),
                url=reverse('post:hashtag_post_list', kwargs={'tag_name': tag_name.replace('#', '')}),
                tag_name=tag_name
            )
            ori_content = re.sub(r'{}(?![<\w])'.format(tag_name), change_tag, ori_content, count=1)
            # content에 포함된 Tag목록을 자신의 tags필드에 추가
            if not self.tags.filter(pk=tag.pk).exists():
                self.tags.add(tag)
        # 편집이 완료된 문자열을 html_content에 저장
        self.html_content = ori_content
        super().save(update_fields=['html_content'])


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_date = models.DateTimeField(auto_now_add=True)


class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return 'Tag({})'.format(self.name)
