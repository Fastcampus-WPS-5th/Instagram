from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class FacebookBackend:
    def authenticate(self, request, facebook_id):
        username = '{}_{}_{}'.format(
            User.USER_TYPE_FACEBOOK,
            settings.FACEBOOK_APP_ID,
            facebook_id,
        )
        try:
            user = User.objects.get(
                user_type=User.USER_TYPE_FACEBOOK,
                username=username
            )
            return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objets.get(pk=user_id)
        except User.DoesNotExist:
            return None
