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
    def _init_validate(self, attribute_list: List[str]) -> None:
        caller_dict = self.__class__.__dict__
        try:
            for attribute_name in attribute_list:
                self._set_attributes(caller_dict[attribute_name])
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
        self._init_validate(REQUIRED_ATTRIBUTES)

    def post(self, request: Request = None) -> Response:
        serializer = self.serializer
        serializer_name = serializer.__name__
        serializer_obj = serializer(data=request.data)

        try:
            serializer_obj.is_valid(raise_exception=True)
            validated_data = serializer_obj.validated_data

            if 'UserRegist' in serializer_name and getattr(serializer_obj, 'create', None):
                serializer_obj.create(validated_data)
            return Response(validated_data, status=self.status)

        except Exception as e:
            logger.warning('post fail')
            raise AuthenticationFail(detail=str(e))


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
        value_from_redis = red.hgetall(key)
    except Exception as e:
        raise RedisProcessError(detail="can't get value") from e
    values = [value for value in value_from_redis.values()]
    return values


def convert_keyname(key: str) -> str:
    return f'{key}_id'
