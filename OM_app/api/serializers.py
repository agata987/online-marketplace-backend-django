from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.utils.translation import ugettext as _

from ..models import *
from ..utils import get_rundom_string

class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class RegisterUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email','password')
        write_only_fields = ('password',)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True    # "required" fields not required (helps with email update only)
        super(UserSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ('id', 'username', 'email','email_verified',)

# NOTE with ModelSerializer in case we want to update password, there will be issues due to hashing before save
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, max_length=128)
    new_password = serializers.CharField(required=True, max_length=128)

    def validate_new_password(self, value):
        validate_password(value)
        return value

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

class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = '__all__'

class OfferCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferCategory
        fields = '__all__'
