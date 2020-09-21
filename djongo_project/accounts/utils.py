import redis

from config.settings import REDIS_CONN_POOL_1
from exceptions.common_exceptions import RedisConnectionError

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


# redis에 token attribute 설정
def set_payload_to_redis(payload: dict = None, black: str = 'False'):
    mappings = {
        'jti': payload['jti'],
        'black': black
    }
    username = payload['username']
    key = convert_keyname(username)
    try:
        red.hmset(key, mappings)
    except redis.exceptions.ConnectionError as ce:
        raise RedisConnectionError(detail=str(ce))


# redis에서 token attribute 가져오기
def get_payload_from_redis(username: str = None) -> list:
    key = convert_keyname(username)
    try:
        val_from_redis = red.hgetall(key)
    except redis.exceptions.ConnectionError as ce:
        raise RedisConnectionError(detail=str(ce))
    values = [value for value in val_from_redis.values()]
    return values


# redis key값 변경
def convert_keyname(key: str) -> str:
    return f'{key}_id'
