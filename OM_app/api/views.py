from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import ObtainJSONWebToken
from datetime import datetime
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from .serializers import *
from ..auth import my_jwt_response_handler
from ..utils import send_verification_email


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Get all user info, update email or delete a user by sending a token.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    # error fix for:
    # Expected view UserDetail to be called with a URL keyword argument named "pk". Fix your URL conf, or set the `.lookup_field` attribute on the view correctly.
    def get_object(self):
        return self.request.user


class MyObtainJSONWebToken(ObtainJSONWebToken):
    """
    Override of ObtainJSONWebToken. Updates the last_login value.
    """
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            token = serializer.object.get('token')
            response_data = my_jwt_response_handler(token, user, request)
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                # support for time-zone is enabled, datetime is stored in UTC
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(
                    api_settings.JWT_AUTH_COOKIE, token, expires=expiration, httponly=True)
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


obtain_jwt_token = MyObtainJSONWebToken.as_view()


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user with a new token.
    """
    serializer = UserSerializerWithToken(data=request.data)
    if serializer.is_valid():
        # creating a user
        serializer.save()

        # sending a verification email
        domain = get_current_site(request).domain
        send_verification_email(serializer.instance.email, serializer.instance.email_verification_hash, domain, serializer.instance.id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmail(generics.GenericAPIView):
    """
    Verify an email with a given verification hash.
    """
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        hash = request.data['hash']
        user = User.objects.get(id=request.data['id'])

        if user.email_verification_hash == hash:
            user.email_verified = True
            user.save(update_fields=['email_verified'])
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)



class SendVerificationEmail(generics.GenericAPIView):
    """
    Send a verification e-mail to a user.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        user = User.objects.get(email=request.data['email'])

        if user and not user.is_authenticated:
            domain = get_current_site(request).domain
            send_verification_email(user.email, user.email_verification_hash, domain, user.id)

            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(generics.UpdateAPIView):
    """
    Change password.
    """
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password hashes the password
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VoivodeshipList(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        voivodeships = Voivodeship.objects.all().order_by('name')
        serializer = VoivodeshipSerializer(voivodeships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CityList(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        cities = City.objects.all().order_by('name')
        name = self.request.query_params.get('name', None)
        if name is not None:
            cities = cities.filter(voivodeship_id=(Voivodeship.objects.get(name=name)))
        serializer = CitySerializer(cities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
