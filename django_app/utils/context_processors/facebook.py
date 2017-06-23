from django.conf import settings


def facebook_info(request):
    context = {
        'facebook_app_id': settings.FACEBOOK_APP_ID
    }
    return context
