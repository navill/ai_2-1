import logging

import redis
from redis.exceptions import ConnectionError
from rest_framework.request import Request
from rest_framework.response import Response

from config.settings import REDIS_CONN_POOL_1
from config.utils import with_retry
from exceptions.api_exception import AuthenticationFail
from exceptions.common_exceptions import RedisProcessError, ClassMisconfiguration

red = redis.StrictRedis(connection_pool=REDIS_CONN_POOL_1)

logger = logging.getLogger('project_logger').getChild(__name__)


class PostMixin:
    def __init__(self):
        required_attributes = ('status', 'serializer')
        parent_dict = self.__class__.__dict__
        parent_name = self.__class__.__name__

        try:
            for attribute in required_attributes:
                _ = parent_dict[attribute]
        except KeyError as ke:
            error_value = str(ke)
            raise ClassMisconfiguration(detail=f"{parent_name} do not have {error_value} attribute")

    def post(self, request: Request = None) -> Response:
        serializer = self.serializer
        serializer_name = serializer.__name__
        serialized_data = serializer(data=request.data)

        try:
            serialized_data.is_valid(raise_exception=True)
            validated_data = serialized_data.validated_data

            if 'UserRegist' in serializer_name and getattr(serialized_data, 'create', None):
                serialized_data.create(validated_data)
            return Response(validated_data, status=self.status)
        except Exception as e:
            logger.warning('post fail')
            raise AuthenticationFail(detail=str(e))


"""
redis 내부 구조
'<username>_id' =  
    {
    'jti': '<jti_token>',    
    'black': '<bool>'
    }
"""


@with_retry(retries_limit=3, allowed_exceptions=ConnectionError)
def set_payload_to_redis(payload: dict = None, black: str = 'False'):
    mappings = {
        'jti': payload['jti'],
        'black': black
    }
    username = payload['username']
    key = convert_keyname(username)

    try:
        red.hmset(key, mappings)
    except Exception as e:
        raise RedisProcessError(detail="can't set value") from e


@with_retry(retries_limit=3, allowed_exceptions=ConnectionError)
def get_payload_from_redis(username: str = None) -> list:
    key = convert_keyname(username)

    try:
        val_from_redis = red.hgetall(key)
    except Exception as e:
        raise RedisProcessError(detail="can't get value") from e
    values = [value for value in val_from_redis.values()]
    return values


def convert_keyname(key: str) -> str:
    return f'{key}_id'
