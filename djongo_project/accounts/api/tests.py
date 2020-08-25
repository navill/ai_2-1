import copy

import pytest
from config import settings

from django.contrib.auth import get_user_model
from accounts.api.serializers import UserRegistSerializer
from accounts.exceptions.api_exception import *
from accounts.exceptions.common_exceptions import *
from accounts.exceptions.user_exception import *

User = get_user_model()
NORMAL_VALUES = {
    'username': 'test123',
    'email': 'test123@test123.com',
    'birth': '1950-12-01',
    'password': 'test12345',
    'password2': 'test12345'
}

EXIST_VALUES = {
    'username': 'test01',
    'email': 'test01@test01.com',
    'birth': '1950-12-01',
    'password': 'test1234',
    'password2': 'test1234'
}


@pytest.fixture
def default_serializer():
    normal_values = copy.deepcopy(NORMAL_VALUES)
    serializer = UserRegistSerializer()
    serializer.validate(normal_values)
    obj = serializer.create(normal_values)

    return obj, serializer,


@pytest.mark.django_db
def test_usercreate(default_serializer):
    user, _ = default_serializer
    assert isinstance(user, User)


@pytest.mark.django_db
def test_password_length_error(client):
    with pytest.raises(NotEnoughPasswordLengthException) as ve:
        values = {
            'username': 'test123',
            'email': 'test123@test123.com',
            'birth': '1950-12-01',
            'password': '1234',
            'password2': '1234'
        }
        serializer = UserRegistSerializer()
        serializer.validate(values)
        serializer.create(values)
    assert 'enough' in str(ve.value)


@pytest.mark.django_db
def test_duplicated_user(client):
    with pytest.raises(ExistObjectException) as eoe:
        for _ in range(2):
            val = copy.deepcopy(NORMAL_VALUES)
            serializer = UserRegistSerializer(val)
            serializer.validate(val)
            serializer.create(val)
    assert 'Exist' in str(eoe.value)


@pytest.mark.django_db
def test_create_ok_user(client):
    val = copy.deepcopy(NORMAL_VALUES)
    serializer = UserRegistSerializer(val)
    serializer.validate(val)
    serializer.create(val)
    assert serializer.to_representation(serializer.data) == {
        'username': 'test123',
        'email': 'test123@test123.com',
        'status': 'ok'
    }


@pytest.mark.django_db
def test_not_match_password(client):
    with pytest.raises(NotMatchPasswordException) as nmpe:
        serializer = UserRegistSerializer()
        serializer.validate(
            {
                'username': 'test123',
                'email': 'test123@test123.com',
                'birth': '1950-12-01',
                'password': 'test12345',
                'password2': 'test54321'
            }
        )
    assert 'match' in str(nmpe.value)


@pytest.mark.django_db
def test_something(client):
    assert 1 is 1
