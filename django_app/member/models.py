from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # 이 User모델을 AUTH_USER_MODEL로 사용하도록 settings.py에 설정
    nickname = models.CharField(max_length=24, null=True, unique=True)

    def __str__(self):
        return self.nickname or self.username
        # return self.nickname if self.nickname else self.username
