import redis
from redis.exceptions import ConnectionError

from config.settings import REDIS_CONN_POOL_1
from config.utils import with_retry, logging, logging_with_level

red = redis.StrictRedis(connection_pool=REDIS_CONN_POOL_1)


def do_post(serializer=None, request=None) -> dict:
    serialized = serializer(data=request.data)

    try:
        serialized.is_valid(raise_exception=True)
        if 'UserRegist' in serialized.__class__.__name__ and getattr(serialized, 'create', None):
            serialized.create(serialized.validated_data)

        return serialized.validated_data
    except Exception:  # create.TypeError, is_valid.ValidationError
        raise


"""
redis 내부 구조
'<username>_id' =  
    {
    'jti': '<jti_token>',    
    'black': '<bool>'
    }
"""


@logging_with_level('warning')
@with_retry(retries_limit=3, allowed_exceptions=ConnectionError)
def set_payload_to_redis(payload: dict = None, black: str = 'False'):
    mappings = {
        'jti': payload['jti'],
        'black': black
    }
    username = payload['username']
    key = convert_keyname(username)
    red.hmset(key, mappings)


@logging_with_level('warning')
@with_retry(retries_limit=3, allowed_exceptions=ConnectionError)
def get_payload_from_redis(username: str = None) -> list:
    key = convert_keyname(username)
    val_from_redis = red.hgetall(key)

    values = [value for value in val_from_redis.values()]
    return values


def convert_keyname(key: str) -> str:
    return f'{key}_id'
