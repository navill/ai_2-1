import logging
from typing import List

import redis
from redis.exceptions import ConnectionError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer, ModelSerializer

from config.settings import REDIS_CONN_POOL_1
from config.utils import with_retry
from exceptions.api_exception import AuthenticationFail
from exceptions.common_exceptions import RedisProcessError, ClassMisconfiguration

red = redis.StrictRedis(connection_pool=REDIS_CONN_POOL_1)

logger = logging.getLogger('project_logger').getChild(__name__)

REQUIRED_ATTRIBUTES = ['required_attributes']


class BaseMixin:
    def _initialize(self, attribute_list: List[str]) -> None:
        try:
            for attribute_name in attribute_list:
                self._set_attributes(self.__class__.__dict__[attribute_name])
        except KeyError as ke:
            key_name = str(ke)
            caller_name = self.__class__.__name__
            raise ClassMisconfiguration(detail=f"{caller_name} do not have {key_name} attribute")

    def _set_attributes(self, attribute_dict) -> None:
        for name, attribute in attribute_dict.items():
            if attribute is not None:
                setattr(self, name, attribute)
            else:
                raise ClassMisconfiguration(detail=f"'{name}' attribute at {self.__class__.__name__} cannot be None!")


class PostMixin(BaseMixin):
    def __init__(self):
        self._initialize(REQUIRED_ATTRIBUTES)

    def post(self, request: Request = None) -> Response:
        serializer = self.serializer
        serializer_obj = serializer(data=request.data)
        serializer_name = serializer.__name__
        caller_name = self.__class__.__name__

        try:
            serializer_obj.is_valid(raise_exception=True)
            validated_data = serializer_obj.validated_data

            if 'UserRegist' in serializer_name and getattr(serializer_obj, 'create', None):
                serializer_obj.create(validated_data)
                logger.info(f'[POST] user is registered by {caller_name}')

            response = Response(validated_data, status=self.status)
            logger.info(f'[POST] excuted {caller_name}')
            return response

        except Exception as e:
            logger.warning(f"[{caller_name}]: {str(e)}")
            raise AuthenticationFail(detail=str(e))


class GetMixin(BaseMixin):
    def __init__(self):
        self._init_validate([])

    def get(self, request, *args, **kwargs):
        return self.serializer


@with_retry(retries_limit=3, allowed_exceptions=ConnectionError)
def set_payload_to_redis(payload: dict, black: str = 'False'):
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
        values_from_redis = red.hgetall(key)
    except Exception as e:
        raise RedisProcessError(detail="can't get value") from e
    return [value for value in values_from_redis.values()]


def convert_keyname(key: str) -> str:
    return f'{key}_id'
