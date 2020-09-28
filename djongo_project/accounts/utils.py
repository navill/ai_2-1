import logging

import redis
from redis.exceptions import ConnectionError

from config.settings import REDIS_CONN_POOL_1
from config.utils import with_retry
from exceptions.api_exception import AuthenticationFail
from exceptions.common_exceptions import RedisProcessError

red = redis.StrictRedis(connection_pool=REDIS_CONN_POOL_1)

logger = logging.getLogger('project_logger').getChild(__name__)


def do_post(serializer=None, request=None) -> dict:
    serialized = serializer(data=request.data)

    try:
        serialized.is_valid(raise_exception=True)
        if 'UserRegist' in serialized.__class__.__name__ and getattr(serialized, 'create', None):
            serialized.create(serialized.validated_data)

        return serialized.validated_data
    except Exception as e:  # create.TypeError, is_valid.ValidationError
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
