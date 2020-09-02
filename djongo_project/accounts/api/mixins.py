from abc import abstractmethod
from datetime import date

from rest_framework_simplejwt.serializers import *

from accounts.constants import User
from accounts.exceptions.api_exception import RegistSerializerValidationException
from accounts.exceptions.user_exception import RegistSerializerException
from accounts.models import Role
from config.utils_log import do_traceback


class RegistSerializerMixin:
    @abstractmethod
    def create(self, validated_data: dict) -> User:
        pass

    def validate(self, attrs: dict) -> dict:
        if self._check_len_password(attrs['password']) and \
                self._check_match_password(attrs['password'], attrs['password2']) and \
                self._check_len_username(attrs['username']):
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
            exc = RegistSerializerException(e)
            raise do_traceback(exc)
        return result

    def to_representation(self, values: dict) -> dict:
        return {
            'username': values['username'],
            'email': values['email'],
            'status': 'ok'
        }

    def _check_len_username(self, username: str) -> bool:
        if len(username) < 6:
            exc = RegistSerializerValidationException({'username': 'Not enough username length(len(username) > 5)'})
            raise do_traceback(exc)
        return True

    def _check_len_password(self, password: str) -> bool:
        if len(password) < 8:
            exc = RegistSerializerValidationException({'password': 'Not enough password length(len(password) > 7'})
            raise do_traceback(exc)
        return True

    def _check_match_password(self, password1: str, password2: str) -> str:
        if password1 != password2:
            exc = RegistSerializerValidationException({'password': "Password does not match"})
            raise do_traceback(exc)
        return password1


class StaffRegistSerializerMixin(RegistSerializerMixin):
    def create(self, validated_data: dict) -> User:
        validated_data['role'] = Role.STAFF
        instance = User.objects.create_user(**validated_data)
        return instance


class RegistSerializerMixin(RegistSerializerMixin):
    def create(self, validated_data: dict) -> User:
        validated_data['role'] = Role.NORMAL
        instance = User.objects.create_user(**validated_data)
        return instance
