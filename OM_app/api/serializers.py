from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.utils.translation import ugettext as _

from ..models import User, Voivodeship, City, Offer
from ..utils import get_rundom_string


jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class CustomJWTSerializer(JSONWebTokenSerializer):
    """
    Enables a user to login with a username or an e-mail.
    """
    username_field = 'username_or_email'

    def validate(self, attrs):

        password = attrs.get("password")
        user_obj = User.objects.filter(email=attrs.get("username_or_email")).first() or User.objects.filter(username=attrs.get("username_or_email")).first()
        if user_obj is not None:
            credentials = {
                'username':user_obj.username,
                'password': password
            }
            if all(credentials.values()):
                user = authenticate(**credentials)
                if user:
                    if not user.is_active:
                        msg = _('User account is disabled.')
                        raise serializers.ValidationError(msg)

                    payload = jwt_payload_handler(user)

                    return {
                        'token': jwt_encode_handler(payload),
                        'user': user
                    }
                else:
                    msg = _('Unable to log in with provided credentials.')
                    raise serializers.ValidationError(msg)

            else:
                msg = _('Must include "{username_field}" and "password".')
                msg = msg.format(username_field=self.username_field)
                raise serializers.ValidationError(msg)

        else:
            msg = _('Account with this email/username does not exists')
            raise serializers.ValidationError(msg)


class UserSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True    # "required" fields not required (helps with email update only)
        super(UserSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ('username', 'email',)

# NOTE used in auth.my_jwt_response_handler
class JWTReponseHandlerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'email_verified',)

# NOTE with ModelSerializer in case we want to update password, there will be issues due to hashing before save
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, max_length=128)
    new_password = serializers.CharField(required=True, max_length=128)

    def validate_new_password(self, value):
        validate_password(value)
        return value

# create a new user with a token
class UserSerializerWithToken(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('token', 'username', 'email', 'password', )

    # user doesn't have an internal 'token' field
    token = serializers.SerializerMethodField()
    # the serializer shouldn't include the submitted password in the returned JSON (write_only)
    password = serializers.CharField(write_only=True, max_length=128)

    # handles password validation
    def validate(self, data):
        user = User(**data)
        password = data.get('password')
        errors = dict()

        try:
            validate_password(password=password, user=user)
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)
        
        if errors:
            raise serializers.ValidationError(errors)
        return super(UserSerializerWithToken, self).validate(data)

    # handles creation of a new token
    def get_token(self, obj):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER   
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(obj)  # data being tokenized (user)
        token = jwt_encode_handler(payload)
        return token

    def create(self, validated_data):
        password = validated_data.pop('password')
        instance = self.Meta.model(**validated_data)
        instance.set_password(password)
        instance.email_verification_hash = get_rundom_string(32)
        instance.save()
        return instance

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'name')
# nested serializer
class VoivodeshipCitiesSerializer(serializers.ModelSerializer):
    cities = CitySerializer(many=True, read_only=True)
    class Meta:
        model = Voivodeship
        fields = ('name', 'cities')
