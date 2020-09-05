from abc import abstractmethod
from datetime import date

from rest_framework_simplejwt.serializers import *

from accounts.constants import User
from accounts.models import Role
from config.utils_log import do_traceback
from exceptions.api_exception import RegistSerializerValidationException


class RegistSerializerMixin:
    errors = {
        'password_match': "Password does not match",
    }

    @abstractmethod
    def create(self, validated_data: dict) -> User:
        pass

    def validate(self, attrs: dict) -> dict:
        # username 및 password 유효성 검사
        if self._check_match_password(attrs['password'], attrs['password2']):
            del attrs['password2']
        return attrs

    def to_internal_value(self, data: dict) -> dict:
        try:
            data = super().to_internal_value(data)

            result = {
                'username': data['username'].lower(),
                'email': data['email'].lower(),
                'password': data['password'],
                'password2': data['password2'],
                'birth': date.fromisoformat(str(data['birth']))
            }
        except Exception as e:
            msg = {}
            for key, val in e.args[0].items():
                value = val[0]
                msg[key] = value.__str__()
                msg[f'{key}_error_code'] = value.code
            raise RegistSerializerValidationException(detail=msg, code='invalid_value')
        return result

    def to_representation(self, values: dict) -> dict:
        return {
            'username': values['username'],
            'email': values['email'],
            'status': 'ok'
        }

    def _check_match_password(self, password1: str, password2: str) -> str:
        if password1 != password2:
            exc = RegistSerializerValidationException(self.errors['password_match'], code='not_match')
            raise do_traceback(exc)
        return password1


# for staff user
class StaffRegistSerializerMixin(RegistSerializerMixin):
    def create(self, validated_data: dict) -> User:
        try:
            validated_data['role'] = Role.STAFF
            instance = User.objects.create_user(**validated_data)
        except Exception as e:
            raise RegistSerializerValidationException(e)
        return instance


# for normal user
class RegistSerializerMixin(RegistSerializerMixin):
    def create(self, validated_data: dict) -> User:
        validated_data['role'] = Role.NORMAL
        instance = User.objects.create_user(**validated_data)
        return instance
