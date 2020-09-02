from abc import abstractmethod

from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token

from accounts.api.tokens.tokens import CustomSlidingToken
from accounts.constants import User
from accounts.exceptions.api_exception import SerializerValidationException
from config.utils_log import do_traceback


class CustomTokenObtainSlidingSerializer(TokenObtainSerializer, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

    @abstractmethod
    def validate(self, attrs: dict) -> dict:
        data = super().validate(attrs)
        token = self.get_token(self.user)
        data['token'] = str(token)
        return data

    @classmethod
    def get_token(cls, user: User) -> Token:
        token = CustomSlidingToken.for_user(user)
        update_last_login(None, user)  # last_login 갱신 위치가 적합한지?
        return token


class CustomTokenRefreshSlidingSerializer(serializers.Serializer):
    token = serializers.CharField()

    @abstractmethod
    def validate(self, attrs: dict) -> dict:

        try:
            token = CustomSlidingToken(attrs['token'])
        except TokenError as te:
            do_traceback(te)
            raise SerializerValidationException(te)

        token.check_exp(api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM)
        token.set_exp()
        attrs['token'] = str(token)

        return attrs


class CustomTokenVerifySerializer(serializers.Serializer):
    token = serializers.CharField()

    @abstractmethod
    def validate(self, attrs: dict) -> dict:

        try:
            CustomSlidingToken(attrs['token'])
        except TokenError as te:
            do_traceback(te)
            raise SerializerValidationException(te)

        return {}


class BlackListTokenSerializer(serializers.Serializer):
    token = serializers.CharField()

    @abstractmethod
    def validate(self, attrs: dict) -> dict:

        try:
            msg = self._do_blacklist(attrs['token'])
        except Exception as e:
            do_traceback(e)
            raise SerializerValidationException(e)

        return {'msg': msg}

    def _do_blacklist(self, token: str) -> str:
        cst = CustomSlidingToken(token)
        cst.blacklist()

        return 'ok'
