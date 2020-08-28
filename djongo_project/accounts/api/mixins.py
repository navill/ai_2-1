from datetime import date

from django.db.models import Q
from rest_framework_simplejwt.serializers import *
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.utils import datetime_from_epoch

from accounts.constants import VALIDATION_TARGETS, User
from accounts.exceptions.api_exception import BlacklistedTokenException
from accounts.models import CustomBlack, CustomOutstanding
from config.utils_log import do_logging


# serializers
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


# tokens
class BlacklistTokenMixin:
    def verify(self):
        self.check_blacklist()
        super().verify()  # check expired time and token type

    def check_blacklist(self):
        jti = self.payload[api_settings.JTI_CLAIM]

        if CustomBlack.objects.filter(token__jti=jti).exists():
            exc = BlacklistedTokenException('This token is blacklisted')
            do_logging('warning', 'WARINING| token is blacklisted', exc=exc)
            raise exc

    def blacklist(self):
        jti = self.payload[api_settings.JTI_CLAIM]
        exp = self.payload['exp']

        token, _ = CustomOutstanding.objects.get_or_create(
            jti=jti,
            defaults={
                'token': str(self),
                'expires_at': datetime_from_epoch(exp),
            },
        )
        do_logging('INFO', 'INFO| complete blacklist')
        return CustomBlack.objects.get_or_create(token=token)

    @classmethod
    def for_user(cls, user: User) -> Token:
        token = super().for_user(user)

        jti = token[api_settings.JTI_CLAIM]
        exp = token['exp']

        CustomOutstanding.objects.create(
            user=user,
            jti=jti,
            token=str(token),
            created_at=token.current_time,
            expires_at=datetime_from_epoch(exp),
        )

        return token
