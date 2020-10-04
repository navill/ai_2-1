from abc import abstractmethod

from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token

from accounts.api.tokens.tokens import CustomSlidingToken
from accounts.constants import User
from accounts.utils import set_payload_to_redis


class CustomTokenObtainSlidingSerializer(TokenObtainSerializer, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

    def validate(self, attrs: dict) -> dict:
        data = super().validate(attrs)
        token = self.get_token(self.user)
        data['token'] = str(token)
        return data

    @classmethod
    def get_token(cls, user: User) -> Token:
        new_token = CustomSlidingToken.for_user(user)
        set_payload_to_redis(payload=new_token.payload, black='False')
        update_last_login(None, user)  # last_login 갱신 위치가 적합한지?
        return new_token


class CustomTokenRefreshSlidingSerializer(serializers.Serializer):
    token = serializers.CharField()

    @abstractmethod
    def validate(self, attrs: dict) -> dict:
        token = CustomSlidingToken(attrs['token'])

        token.check_exp(api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM)
        token.set_exp()

        set_payload_to_redis(payload=token.payload)
        attrs['token'] = str(token)
        return attrs


class CustomTokenVerifySerializer(serializers.Serializer):
    token = serializers.CharField()

    @abstractmethod
    def validate(self, attrs: dict) -> dict:
        CustomSlidingToken(attrs['token'])
        return {}


class BlackListTokenSerializer(serializers.Serializer):
    token = serializers.CharField()

    @abstractmethod
    def validate(self, attrs: dict) -> dict:
        msg = self._do_blacklist(attrs['token'])
        return {'msg': msg}

    def _do_blacklist(self, token: str) -> str:
        cst = CustomSlidingToken(token)
        cst.blacklist()
        return 'ok'
