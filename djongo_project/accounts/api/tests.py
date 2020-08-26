import copy

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from accounts.api.serializers import UserRegistSerializer
from accounts.api.tokens.tokens import CustomSlidingToken
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


"""
Fixtures - API
"""


# get api client object
@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


# create MyUser object
@pytest.fixture
def create_user(db, django_user_model):
    def make_user(**kwargs):
        if 'username' not in kwargs:
            kwargs['username'] = 'admin'
        if 'email' not in kwargs:
            kwargs['email'] = 'admin@admin.com'
        if 'password' not in kwargs:
            kwargs['password'] = 'test1234'
        if 'birth' not in kwargs:
            kwargs['birth'] = '1988-01-01'
        return django_user_model.objects.create_user(**kwargs)

    return make_user


# get test user
@pytest.fixture
def get_user(create_user):
    return create_user()


# create Sliding Token
@pytest.fixture
def create_token(get_user):
    user = get_user
    token = CustomSlidingToken.for_user(user)
    return token


# authenticate user
@pytest.fixture
def api_client_with_credentials(get_user, api_client):
    user = get_user
    api_client.force_authenticate(user=user)
    yield api_client
    api_client.force_authenticate(user=None)


# get login info
@pytest.fixture
def login_info():
    return {'username': 'admin', 'password': 'test1234'}


"""
Do Test - API
"""


# create test user
@pytest.mark.django_db
def test_create_user(create_user):
    user = create_user()
    assert user.username == 'admin'


# get token with test user
@pytest.mark.django_db
def test_get_token(api_client_with_credentials, login_info):
    url = reverse('api:login')
    response = api_client_with_credentials.post(url, data=login_info)
    assert response.status_code == 201
    assert 'token' in response.json()


# verify valid token
@pytest.mark.django_db
def test_verify_token(api_client_with_credentials, create_token):
    url = reverse('api:verify')
    token = create_token
    data = {'token': str(token)}
    response = api_client_with_credentials.post(url, data=data)
    assert response.status_code == 200
    assert {} == response.json()
