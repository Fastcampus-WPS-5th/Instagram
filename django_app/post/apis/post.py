from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Post
from ..serializers import PostSerializer

__all__ = (
    'PostListView',
)


class PostListView(APIView):
    # get요청이 왔을 때, Post.objects.all()을
    # PostSerailizer를 통해 Response로 반환
    # DRF API Guide
    #   - API View
    #   - Serializers
    def get(self, request, *args, **kwargs):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
