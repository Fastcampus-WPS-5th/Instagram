import re

import requests
from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager as DefaultUserManager
from django.core.files.temp import NamedTemporaryFile
from django.db import models

from utils.fields import CustomImageField


class UserManager(DefaultUserManager):
    def get_or_create_facebook_user(self, user_info):
        username = '{}_{}_{}'.format(
            self.model.USER_TYPE_FACEBOOK,
            settings.FACEBOOK_APP_ID,
            user_info['id']
        )
        user, user_created = self.get_or_create(
            username=username,
            user_type=self.model.USER_TYPE_FACEBOOK,
            defaults={
                'last_name': user_info.get('last_name', ''),
                'first_name': user_info.get('first_name', ''),
                'email': user_info.get('email', ''),
            }
        )
        # 유저가 새로 생성되었을 때만 프로필 이미지를 받아옴
        if user_created and user_info.get('picture'):
            # https://scontent.xx.fbcdn.net/v/t1.0-1/p50x50/17190366_634177590104859_7473999312831140266_n.jpg?oh=4c68d08b4066747c1c7c7bcb32670b6a&oe=59DA648E
            # 프로필 이미지 URL
            url_picture = user_info['picture']['data']['url']
            # 파일확장자를 가져와서, 유저고유의 파일명을 만들어줌
            p = re.compile(r'.*\.([^?]+)')
            file_ext = re.search(p, url_picture).group(1)
            file_name = '{}.{}'.format(
                user.pk,
                file_ext
            )
            # Python tempfile
            # https://docs.python.org/3/library/tempfile.html
            # 이미지파일을 임시저장할 파일객체
            temp_file = NamedTemporaryFile()
            # 프로필 이미지 URL에 대한 get요청 (이미지 다운로드)
            response = requests.get(url_picture)
            # 요청 결과를 temp_file에 기록
            temp_file.write(response.content)
            # ImageField의 save()메서드를 호출해서 해당 임시파일객체를 주어진 이름의 파일로 저장
            # 저장하는 파일명은 위에서 만든 <유저pk.주어진파일확장자> 를 사용
            user.img_profile.save(file_name, temp_file)
        return user


class User(AbstractUser):
    """
    동작
        follow : 내가 다른사람을 follow함
        unfollow : 내가 다른사람에게 한 follow를 취소함

    속성
        followers : 나를 follow하고 있는 사람들
        follower : 나를 follow하고 있는 사람
        following : 내가 follow하고 있는 사람들
        friend : 나와 서로 follow하고 있는 관계
        friends : 나와 서로 follow하고 있는 모든 관계
        없음 : 내가 follow하고 있는 사람 1명
            (나는 저 사람의 follower이다 또는 나는 저 사람을 follow하고 있다 라고 표현)

    ex) 내가 박보영, 최유정, 고성현을 follow하고 고성현과 김수정은 나를 follow한다
        나의 followers는 고성현, 김수정
        나의 following은 박보영, 최유정
        김수정은 나의 follower이다
        나는 박보영의 follower다
        나와 고성현은 friend관계이다
        나의 friends는 고성현 1명이다
    """
    # 이 User모델을 AUTH_USER_MODEL로 사용하도록 settings.py에 설정
    USER_TYPE_DJANGO = 'd'
    USER_TYPE_FACEBOOK = 'f'
    USER_TYPE_CHOICES = (
        (USER_TYPE_DJANGO, 'Django'),
        (USER_TYPE_FACEBOOK, 'Facebook'),
    )
    # 유저타입. 기본은 Django이며, 페이스북 로그인시 USER_TYPE_FACEBOOK값을 갖도록 함
    user_type = models.CharField(max_length=1, choices=USER_TYPE_CHOICES, default=USER_TYPE_DJANGO)
    nickname = models.CharField(max_length=24, null=True, unique=True)
    img_profile = CustomImageField(
        upload_to='user',
        blank=True,
        # default_static_image='images/profile.png',
    )
    relations = models.ManyToManyField(
        'self',
        through='Relation',
        symmetrical=False,
    )

    # 위에서 만든 CustomUserManager를 objects속성으로 사용
    # User.objects.create_facebook_user()메서드 실행 가능
    objects = UserManager()

    def __str__(self):
        return self.nickname or self.username
        # return self.nickname if self.nickname else self.username

    def follow(self, user):
        # 매개변수로 전달된 user의 형(타입,=클래스) 검사
        if not isinstance(user, User):
            raise ValueError('"user" argument must <User> class')
        # 해당 user를 follow하는 Relation을 생성한다
        # 이미 follow상태일경우 아무일도 하지 않음

        # self로 주어진 User로부터 Relation의 from_user에 해당하는 RelatedManager를 사용
        self.follow_relations.get_or_create(
            to_user=user
        )

        # Relation모델의 매니저를 사용
        Relation.objects.get_or_create(
            from_user=self,
            to_user=user
        )

        # user로 주어진 User로부터 Relation의 to_user에 해당하는 RelatedManager를 사용
        user.follower_relations.get_or_create(
            from_user=self
        )

    def unfollow(self, user):
        # 위의 반대 역할
        Relation.objects.filter(
            from_user=self,
            to_user=user
        ).delete()

    def is_follow(self, user):
        # 해당 user를 내가 follow하고 있는지 bool여부를 반환
        # ModelManager.exists()
        return self.follow_relations.filter(to_user=user).exists()

    def is_follower(self, user):
        # 해당 user가 나를 follow하고 있는지 bool여부를 반환
        return self.follower_relations.filter(from_user=user).exists()

    def follow_toggle(self, user):
        # 이미 follow상태면 unfollow로, 아닐경우 follow상태로 만듬
        relation, relation_created = self.follow_relations.get_or_create(to_user=user)
        if not relation_created:
            relation.delete()
        else:
            return relation

    @property
    def following(self):
        # https://docs.djangoproject.com/en/1.11/ref/models/querysets/#in
        relations = self.follow_relations.all()
        return User.objects.filter(pk__in=relations.values('to_user'))

    @property
    def followers(self):
        relations = self.follower_relations.all()
        return User.objects.filter(pk__in=relations.values('from_user'))


class Relation(models.Model):
    from_user = models.ForeignKey(User, related_name='follow_relations')
    to_user = models.ForeignKey(User, related_name='follower_relations')
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Relation from({}) to ({})'.format(
            self.from_user,
            self.to_user
        )

    class Meta:
        unique_together = (
            ('from_user', 'to_user'),
        )
