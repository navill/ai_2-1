import redis
from redis.exceptions import ConnectionError

from config.settings import REDIS_CONN_POOL_1
from exceptions.common_exceptions import RedisProcessError
from utilities.common_utils import with_retry

red = redis.StrictRedis(connection_pool=REDIS_CONN_POOL_1)


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
