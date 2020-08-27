from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSlidingSerializer, \
    TokenVerifySerializer, TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token

from accounts.api.tokens.tokens import CustomSlidingToken
from accounts.constants import User
from accounts.exceptions.api_exception import DoNotRefreshTokenException, DoNotVerifyTokenException


class CustomTokenObtainSlidingSerializer(TokenObtainSerializer, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = []

    def validate(self, attrs: dict) -> dict:
        data = super().validate(attrs)  # authenticate
        token = self.get_token(self.user)
        data['token'] = str(token)
        return data

    @classmethod
    def get_token(cls, user: User) -> Token:
        return CustomSlidingToken.for_user(user)


class CustomTokenRefreshSlidingSerializer(TokenRefreshSlidingSerializer, serializers.ModelSerializer):
    token = serializers.CharField()

    class Meta:
        model = User
        fields = ['token']

    def validate(self, attrs: dict) -> dict:
        try:
            token = CustomSlidingToken(attrs['token'])
        except TokenError as te:
            raise DoNotRefreshTokenException(te)
        token.check_exp(api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM)
        token.set_exp()
        return {'token': str(token)}


class CustomTokenVerifySerializer(TokenVerifySerializer, serializers.ModelSerializer):
    token = serializers.CharField()

    class Meta:
        model = User
        fields = ['token']

    def validate(self, attrs: dict) -> dict:
        try:
            token = CustomSlidingToken(attrs['token'])
            token.check_blacklist()
        except TokenError as te:
            raise DoNotVerifyTokenException(te)
        return {}
