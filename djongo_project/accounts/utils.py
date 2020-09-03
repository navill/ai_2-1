from typing import Generator

import redis
from django.conf import settings

from accounts.constants import STATUS
from accounts.exceptions.user_exception import RegistSerializerException
from config.settings import REDIS_CONN_POOL_1
from config.utils_log import do_traceback

red = redis.StrictRedis(connection_pool=REDIS_CONN_POOL_1)


def do_post(serializer=None, request=None, stat=None) -> tuple:
    serialized = serializer(data=request.data)

    try:
        if serialized.is_valid():  # if is_valid is false, raise serializers.ValidationError
            msg = serialized.validated_data
            # ininstance는 임포트 에러때문에 불가 -> baseserializer를 별도의 폴더에 둘 경우 가능
            if 'UserRegist' in serialized.__class__.__name__ and getattr(serialized, 'create', None):
                serialized.create(serialized.validated_data)
                msg = serialized.data  # data = to_representation()
            return msg, stat
    except Exception as e:
        if not settings.DEBUG:
            do_traceback(e)
            if isinstance(e, RegistSerializerException):
                msg = {}
                for key, val in e.__context__.args[0].items():
                    msg[key] = str(val[0])  # {key:str(val[0])})
                e = msg
        else:
            raise
        return {'do_post Error': str(e)}, STATUS['400'],


"""
redis 내부 구조
'askdlfjalsjdr333' =  
    {
    'username': admin,    
    'black': 'False'
    }
"""


def set_token_to_redis(**kwargs: str):
    """
    :param kwargs: username: str, jti: str, black: str
    """
    username = kwargs.pop('username')
    key = convert_keyname(username)
    red.hmset(key, kwargs)


def get_token_from_redis(username: str = None):
    key = convert_keyname(username)
    val_from_redis = red.hgetall(key)
    values = (value for value in val_from_redis.values())
    return values


def convert_keyname(key: str) -> str:
    return f'{key}_id'
