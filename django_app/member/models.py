from django.contrib.auth.models import AbstractUser
from django.db import models


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
    nickname = models.CharField(max_length=24, null=True, unique=True)
    relations = models.ManyToManyField(
        'self',
        through='Relation',
        symmetrical=False,
    )

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
