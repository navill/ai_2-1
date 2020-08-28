from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token

from accounts.api.tokens.tokens import CustomSlidingToken
from accounts.constants import User
from accounts.exceptions.api_exception import DoNotRefreshTokenException, DoNotVerifyTokenException
from config.settings import REDIS_OBJ

red = REDIS_OBJ


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
        token = CustomSlidingToken.for_user(user)
        update_last_login(None, user)  # last_login 갱신 위치가 적합한지?
        return token


class CustomTokenRefreshSlidingSerializer(serializers.ModelSerializer):
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


class CustomTokenVerifySerializer(serializers.ModelSerializer):
    token = serializers.CharField()

    class Meta:
        model = User
        fields = ['token']

    def validate(self, attrs: dict) -> dict:
        try:
            token = CustomSlidingToken(attrs['token'])
            # print(token.payload)
        except TokenError as te:
            raise DoNotVerifyTokenException(te)
        # set_token_to_redis(token.payload)
        # token.check_exp(api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM)
        # token.set_exp()
        token.check_blacklist()

        return {}
