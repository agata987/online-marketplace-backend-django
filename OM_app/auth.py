from .models import User
from django.contrib.auth.backends import ModelBackend
from .api.serializers import UserSerializer, JWTReponseHandlerSerializer
"""
For override auth settings.
"""

def my_jwt_response_handler(token, user=None, request=None):
    """
    When a user logs in, they receive their token but not any of their user data.
    That's a custom fuction to override JWT default settings.
    """
    return {
        'token': token,
        'user': JWTReponseHandlerSerializer(user, context={'request': request}).data
    }
