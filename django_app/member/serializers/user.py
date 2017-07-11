from rest_framework import serializers
from ..models import User

__all__ = (
    'UserSerializer',
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'pk',
            'username',
        )

# serializers의 __init__파일 구현
# urls에 urls_apis, urls_views로 파일 구분
# apis에 user.py모듈 생성, UserDetailView구현
#   urls.urls_apis에 UserDetailView.as_view()를 연결

# config.urls.urls_apis에 member.urls.urls_apis를 연결