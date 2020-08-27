from datetime import date

from django.db.models import Q
from rest_framework.request import Request
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import *

from accounts.api.tokens.tokens import CustomSlidingToken
from accounts.constants import VALIDATION_TARGETS, User
from config.utils_log import do_logging


class RegisterMixin(ModelSerializer):
    def create(self, validated_data: dict) -> User:
        password = self._del_password(validated_data)
        user = self.Meta.model(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def validate(self, attrs: dict) -> dict:
        if self._check_len_password(attrs['password']) and \
                self._check_match_passwords(attrs['password'], attrs['password2']):
            return self._validate_exist(attrs, targets=VALIDATION_TARGETS)

    def to_internal_value(self, data: dict) -> dict:
        data = super().to_internal_value(data)
        try:
            result = {
                'username': data['username'].lower(),
                'email': data['email'].lower(),
                'password': data['password'],
                'password2': data['password2'],
                'birth': date.fromisoformat(str(data['birth']))
            }
        except Exception as e:
            raise serializers.ValidationError(e)
        return result

    def to_representation(self, values: dict) -> dict:
        return {
            'username': values['username'],
            'email': values['email'],
            'status': 'ok'
        }

    def _validate_exist(self, attrs: dict, targets: tuple = None) -> dict:
        targets, q = targets, Q()
        for target in targets:
            q |= Q(**{target: attrs[target]})
        obj = User.objects.filter(q)
        if obj.exists():
            exc = serializers.ValidationError({'_validate_exist': "Exist object"})
            do_logging('error', 'ERROR| if obj.exists() == True', exc=exc)
            raise exc
        return attrs

    def _check_len_password(self, password: str) -> bool:
        if len(password) < 8:
            exc = serializers.ValidationError({'_check_len_password': 'Not enough password length'})
            do_logging('error', 'ERROR| if len(password) < 8 == True', exc=exc)
            raise exc
        return True

    def _check_match_passwords(self, password1: str, password2: str) -> str:
        if password1 != password2:
            exc = serializers.ValidationError({'_check_match_password': "Password do not match."})
            do_logging('error', 'ERROR| if password1 != password2 == True', exc=exc)
            raise exc
        return password1

    def _del_password(self, validated_data):
        del validated_data['password2']
        password = validated_data.pop('password')
        return password


class BlackMixin:
    def get_sliding_token(self, request: Request) -> CustomSlidingToken:
        try:
            sliding_token = request.data['token']
            sliding_token = CustomSlidingToken(sliding_token)  # SlidingToken call -> check_blacklist()
        except KeyError as ke:
            exc = serializers.ValidationError(ke)
            do_logging('error', 'ERROR| sliding token key error', exc=exc)
            raise exc
        return sliding_token

    def regist_blacklist(self, token: CustomSlidingToken):
        try:
            token.check_blacklist()
        except TokenError as te:
            exc = serializers.ValidationError(te)
            do_logging('error', 'ERROR| TokenError from check_blacklist', exc=exc)
            raise exc
        token.blacklist()
