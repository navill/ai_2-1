from datetime import date

from django.db.models import Q
from rest_framework.request import Request
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import *

from accounts.api.tokens.tokens import CustomSlidingToken
from accounts.constants import VALIDATION_TARGETS, User
from accounts.exceptions.api_exception import WithoutTokenException, InvalidTokenException
from accounts.exceptions.common_exceptions import ExistObjectException
from accounts.exceptions.user_exception import NotEnoughPasswordLengthException, NotMatchPasswordException


# logger = logging.getLogger(__name__)

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
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        password2 = data.get('password2')
        birth = data.get('birth')
        try:
            result = {
                'username': username.lower(),
                'email': email.lower(),
                'password': password,
                'password2': password2,
                'birth': date.fromisoformat(birth)
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
        # for attr, value in attrs.items():
        #     if attr in targets:
        #         q |= Q(**{attr: value})
        for target in targets:
            q |= Q(**{target: attrs[target]})
        obj = User.objects.filter(q)
        if obj.exists():
            exc = ExistObjectException("Exist object")
            # do_logging(info='if obj.exists() == True', exc=exc)
            raise exc
        return attrs

    def _check_len_password(self, password: str) -> bool:
        if len(password) < 8:
            exc = NotEnoughPasswordLengthException('Not enough password length')
            # do_logging(info='if len(password) < 8 == True', exc=exc)
            raise exc
        return True

    def _check_match_passwords(self, password1: str, password2: str) -> str:
        if password1 != password2:
            exc = NotMatchPasswordException("Password do not match.")
            # do_logging(info='if password1 != password2 == True', exc=exc)
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
            raise WithoutTokenException(ke)
        return sliding_token

    def regist_blacklist(self, token: CustomSlidingToken):
        try:
            token.check_blacklist()
        except TokenError as te:
            raise InvalidTokenException(te)
        token.blacklist()
