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

    def __str__(self):
        return self.nickname or self.username
        # return self.nickname if self.nickname else self.username
