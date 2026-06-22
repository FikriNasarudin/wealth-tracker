from rest_framework import serializers
from django.contrib.auth import get_user_model
from google.oauth2 import id_token
from google.auth.transport import requests

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'first_name', 'last_name')
        extra_kwargs = {'username': {'required': False}}

    def create(self, validated_data):
        email = validated_data['email']
        user = User.objects.create_user(
            email=email,
            username=validated_data.get('username', email),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class GoogleAuthSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, token):
        try:
            # We don't enforce CLIENT_ID here for simplicity, but in production we should
            idinfo = id_token.verify_oauth2_token(token, requests.Request())
            return idinfo
        except ValueError:
            raise serializers.ValidationError("Invalid Google token")
