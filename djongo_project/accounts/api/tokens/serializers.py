from abc import abstractmethod
from typing import *

from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token

from accounts.api.tokens.tokens import CustomSlidingToken
from accounts.constants import User
from utilities.account_utils import set_payload_to_redis


class CustomTokenObtainSlidingSerializer(TokenObtainSerializer, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

    def validate(self, attrs: Dict) -> Dict:
        data = super().validate(attrs)
        token = self.get_token(self.user)
        data['token'] = str(token)
        return data

    @classmethod
    def get_token(cls, user: User) -> Type[Token]:
        new_token = CustomSlidingToken.for_user(user)
        set_payload_to_redis(payload=new_token.payload, black='False')
        update_last_login(None, user)
        return new_token


class CustomTokenRefreshSlidingSerializer(serializers.Serializer):
    token = serializers.CharField()

    @abstractmethod
    def validate(self, attrs: Dict) -> Dict:
        token = CustomSlidingToken(attrs['token'])

        token.check_exp(api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM)
        token.set_exp()

        set_payload_to_redis(payload=token.payload)
        attrs['token'] = str(token)
        return attrs


class CustomTokenVerifySerializer(serializers.Serializer):
    token = serializers.CharField()

    @abstractmethod
    def validate(self, attrs: Dict) -> Dict:
        CustomSlidingToken(attrs['token'])
        return {}


class BlackListTokenSerializer(serializers.Serializer):
    token = serializers.CharField()

    @abstractmethod
    def validate(self, attrs: Dict) -> Dict:
        self._do_blacklist(attrs['token'])
        return {'msg': 'ok'}

    def _do_blacklist(self, token: str) -> None:
        token_obj = CustomSlidingToken(token)
        token_obj.blacklist()
