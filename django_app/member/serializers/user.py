from rest_framework import serializers
from ..models import User

__all__ = (
    'UserSerializer',
    'UserCreationSerializer',
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'pk',
            'username',
            'nickname',
        )


class UserCreationSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=100,
    )
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_username(self, username):
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError('Username already exist')
        return username

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError('Passwords didn\'t match')
        return data

    def save(self, *args, **kwargs):
        username = self.validated_data.get('username', '')
        password = self.validated_data.get('password1', '')
        user = User.objects.create_user(
            username=username,
            password=password
        )
        return user



    # serializers의 __init__파일 구현
    # urls에 urls_apis, urls_views로 파일 구분
    # apis에 user.py모듈 생성, UserDetailView구현
    #   urls.urls_apis에 UserRetrieveUpdateDestroyView.as_view()를 연결
    # config.urls.urls_apis에 member.urls.urls_apis를 연결
