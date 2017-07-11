from rest_framework import serializers

from member.serializers import UserSerializer
from ..serializers.comment import CommentSerializer
from ..models import Post


__all__ = (
    'PostSerializer',
)


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    # 아래 코드가 동작하도록 CommentSerializer를 구현
    my_comment = CommentSerializer(read_only=True)

    class Meta:
        model = Post
        fields = (
            'pk',
            'author',
            'photo',
            'my_comment',
        )
        read_only_fields = (
            'author',
            'my_comment',
        )

