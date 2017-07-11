from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.permissions import ObjectIsRequestUser
from ..models import User
from ..serializers import UserSerializer

__all__ = (
    'UserRetrieveUpdateDestroyView',
)


# UserListCreateView
# generics.ListCreateAPIView사용
#  다 하셨으면 두 APIView를 Postman에 등록 후 테스트
#   List, Create, Retrieve, Update, Destroy전부ㄴ
class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        ObjectIsRequestUser,
    )
