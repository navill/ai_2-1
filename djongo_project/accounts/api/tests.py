import copy

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.exceptions import ValidationError

from accounts.api.serializers import UserRegistSerializer
from accounts.api.tokens.tokens import CustomSlidingToken

"""
Serializer module test
"""
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
    normal_data = copy.deepcopy(NORMAL_VALUES)
    serializer = UserRegistSerializer()
    serializer.validate(normal_data)
    obj = serializer.create(normal_data)

    return obj, serializer,


@pytest.mark.django_db
def test_usercreate(default_serializer):
    user, _ = default_serializer
    assert isinstance(user, User)


@pytest.mark.django_db
def test_password_length_error(client):
    with pytest.raises(ValidationError) as ve:
        data = {
            'username': 'test123',
            'email': 'test123@test123.com',
            'birth': '1950-12-01',
            'password': '1234',
            'password2': '1234'
        }
        serializer = UserRegistSerializer()
        serializer.validate(data)
        serializer.create(data)
    assert 'enough' in str(ve.value)


@pytest.mark.django_db
def test_duplicated_user(client):
    with pytest.raises(ValidationError) as eoe:
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
    with pytest.raises(ValidationError) as nmpe:
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
@pytest.mark.parametrize(
    'username, email, birth, password, password2, status_code', [
        # normal
        ('admin', 'admin@admin.com', '1988-01-01', 'test1234', 'test1234', 201),
        # without username
        ('', 'admin@admin.com', '1988-01-01', 'test1234', 'test1234', 400),
        # without email
        ('admin', '', '1988-01-01', 'test1234', 'test1234', 400),
        # invalid email
        ('admin', 'adminadmincom', '1988-01-01', 'test1234', 'test1234', 400),
        # not engough password length
        ('admin', 'admin@admin.com', '1988-01-01', 'test123', 'test123', 400),
        # not match password
        ('admin', 'admin@admin.com', '1988-01-01', 'test1234', '1234test', 400),
    ]
)
def test_create_user(api_client, username, email, birth, password, password2, status_code):
    url = reverse('api:regist')
    data = {
        'username': username,
        'email': email,
        'birth': birth,
        'password': password,
        'password2': password2
    }
    response = api_client.post(url, data=data)
    assert response.status_code == status_code


# get token with test user
@pytest.mark.django_db
def test_get_token(api_client_with_credentials, login_info):
    url = reverse('api:login')
    response = api_client_with_credentials.post(url, data=login_info)
    assert response.status_code == 201
    assert 'token' in response.json()


# verify valid token
@pytest.mark.django_db
def test_verify_token(api_client, create_token):
    url = reverse('api:verify')
    token = create_token
    data = {'token': str(token)}
    response = api_client.post(url, data=data)
    assert response.status_code == 200
    assert {} == response.json()


@pytest.mark.django_db
def test_check_blacklist_token(api_client, create_token):
    url = reverse('api:logout')
    token = create_token
    data = {'token': str(token)}
    response = api_client.post(url, data=data)
    assert response.status_code == 200
    assert {'status': 'ok'} == response.json()
