from rest_framework.reverse import reverse as api_reverse
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import *

from accounts.api.mixins import RegistSerializerMixin
from accounts.constants import User


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


# class GroupSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = GroupMap
#         fields = ('url', 'user', 'group', 'date_joined')


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'id', 'username')

    def get_url(self, obj: User):
        request = self.context['request']
        return api_reverse('api-user:detail', kwargs={'username': obj.username}, request=request)


class UserRegistSerializer(RegistSerializerMixin, serializers.ModelSerializer):
    username = serializers.CharField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    birth = serializers.DateField(required=True)
    password = serializers.CharField(min_length=8, write_only=True, required=True)
    password2 = serializers.CharField(min_length=8, write_only=True, required=True)

    # password = PasswordField(write_only=True)
    # password2 = PasswordField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'birth')

    def validate(self, attrs):
        validated_attrs = super().validate(attrs)
        return validated_attrs


class UserProfileRegister(serializers.ModelSerializer):
    address = serializers.CharField()
    sex = serializers.CharField()
    description = serializers.CharField()
