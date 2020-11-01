from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from ..models import *

# user
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password')
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True}
        }
    
    def save(self):
        user = User (
            email=self.validated_data['email'],
            username=self.validated_data['username']
        )
        errors = dict()
        try:
            validate_password(password=self.validated_data['password'], user=user)
        except ValidationError as e:
            errors['password'] = list(e.messages)
        
        if errors:
            raise serializers.ValidationError(errors)
        else:
            password=self.validated_data['password']
            user.set_password(password)
            user.save()
        return user
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
