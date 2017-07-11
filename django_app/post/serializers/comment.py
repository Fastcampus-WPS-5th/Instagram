from rest_framework import serializers

from ..models import Comment

__all__ = (
    'CommentSerializer',
)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            'pk',
            'author',
            'post',
            'content',
            'created_date',
        )
        read_only_fields = (
            'created_date',
        )
