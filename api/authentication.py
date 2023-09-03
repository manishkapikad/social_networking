import datetime
from django.conf import settings
from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions


class TokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')
        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')
        if token.created < datetime.datetime.now() - datetime.timedelta(
           hours=getattr(settings, 'REST_FRAMEWORK_TOKEN_EXPIRE_HOURS', 24)):
            raise exceptions.AuthenticationFailed('Token has expired')
        return (token.user, token)
