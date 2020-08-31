from datetime import date

from django.db.models import Q
from rest_framework_simplejwt.serializers import *
from rest_framework_simplejwt.tokens import Token

from accounts.constants import VALIDATION_TARGETS, User
from accounts.utils import get_token_from_redis, set_token_to_redis
# serializers
from config.utils_log import do_traceback


class RegistSerializerMixin:
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
            do_traceback()
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
            do_traceback()
            raise exc
        return attrs

    def _check_len_password(self, password: str) -> bool:
        if len(password) < 8:
            exc = serializers.ValidationError({'_check_len_password': 'Not enough password length'})
            do_traceback()
            raise exc
        return True

    def _check_match_passwords(self, password1: str, password2: str) -> str:
        if password1 != password2:
            exc = serializers.ValidationError({'_check_match_password': "Password do not match."})
            do_traceback()
            raise exc
        return password1

    def _del_password(self, validated_data):
        del validated_data['password2']
        password = validated_data.pop('password')
        return password


# tokens
class BlacklistTokenMixin:
    def verify(self):
        super().verify()  # check expired time and token type
        self.check_blacklist()

    def check_blacklist(self):
        jti = self.payload[api_settings.JTI_CLAIM]
        # if CustomBlack.objects.filter(token__jti=jti).exists():
        token_from_redis = get_token_from_redis(self.payload)
        if token_from_redis == jti:
            do_traceback()
            raise serializers.ValidationError('This token is already blacklisted')

    def blacklist(self):
        set_token_to_redis(self.payload)

    @classmethod
    def for_user(cls, user: User) -> Token:
        token = super().for_user(user)
        return token
