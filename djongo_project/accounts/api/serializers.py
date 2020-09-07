from datetime import date

from rest_framework.reverse import reverse as api_reverse
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import *

from accounts.constants import User
from accounts.models import Role
from config.utils_log import do_traceback
from exceptions.api_exception import RegistSerializerValidationException


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'groups')


class AuthTestSerializer(TokenRefreshSlidingSerializer, serializers.HyperlinkedModelSerializer):
    username = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username',)

    def validate(self, attrs):
        return super(AuthTestSerializer, self).validate(attrs)


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'id', 'username')

    def get_url(self, obj: User):
        request = self.context['request']
        return api_reverse('api-user:detail', kwargs={'username': obj.username}, request=request)


class BaseRegistSerializer(serializers.ModelSerializer):
    username = serializers.CharField(min_length=4, max_length=16, required=True,
                                     validators=[UniqueValidator(queryset=User.objects.all())])
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    birth = serializers.DateField(required=True)
    password = serializers.CharField(min_length=8, max_length=16, write_only=True, required=True)
    password2 = serializers.CharField(min_length=8, max_length=16, write_only=True, required=True)

    errors = {
        'password_match': "Password does not match",
    }

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'birth')

    def create(self, validated_data: dict) -> User:
        try:
            instance = User.objects.create_user(**validated_data)
        except Exception as e:
            # error_msg = field에 정의된 조건에 맞는 validation message
            raise RegistSerializerValidationException(e)
        return instance

    def validate(self, attrs: dict) -> dict:
        # username 및 password 유효성 검사
        if self._check_match_password(attrs['password'], attrs['password2']):
            del attrs['password2']
        return attrs

    def to_internal_value(self, data: dict) -> dict:
        try:
            data = super().to_internal_value(data)  # -> ValidationError

            result = {
                'username': data['username'].lower(),
                'email': data['email'].lower(),
                'password': data['password'],
                'password2': data['password2'],
                'birth': date.fromisoformat(str(data['birth']))
            }
        except Exception as e:
            msg = self._convert_exc_msg(e)
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

    def _convert_exc_msg(self, exc: Exception = None) -> dict:
        msg = {}
        for key, val in exc.args[0].items():
            value = val[0]
            msg[key] = value.__str__()
            msg[f'{key}_code'] = value.code
        return msg


class UserRegistSerializer(BaseRegistSerializer):
    def create(self, validated_data: dict) -> User:
        return super().create(validated_data)

    def validate(self, attrs):
        return super().validate(attrs)


class StaffUserRegistSerializer(BaseRegistSerializer):
    def create(self, validated_data: dict) -> User:
        validated_data['role'] = Role.STAFF
        return super().create(validated_data)

    def validate(self, attrs):
        return super().validate(attrs)


class UserProfileRegister(serializers.ModelSerializer):
    address = serializers.CharField()
    sex = serializers.CharField()
    description = serializers.CharField()
