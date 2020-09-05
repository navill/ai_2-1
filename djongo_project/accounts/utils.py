import redis

from config.settings import REDIS_CONN_POOL_1

red = redis.StrictRedis(connection_pool=REDIS_CONN_POOL_1)


def do_post(serializer=None, request=None) -> dict:
    serialized = serializer(data=request.data)

    try:
        # if is_valid is false, raise serializers.ValidationError
        if serialized.is_valid(raise_exception=True):
            msg = serialized.validated_data

            # ininstance는 임포트 에러때문에 불가 -> baseserializer를 별도의 폴더에 둘 경우 가능
            if 'UserRegist' in serialized.__class__.__name__ and getattr(serialized, 'create', None):
                serialized.create(serialized.validated_data)
                msg = serialized.data
            return msg
    except Exception:
        raise


"""
redis 내부 구조
'askdlfjalsjdr333' =  
    {
    'username': admin,    
    'black': 'False'
    }
"""


# redis에 token attribute 설정
def set_token_to_redis(payload=None, black='False'):
    mappings = {
        'jti': payload['jti'],
        'black': str(black)
    }
    username = payload['username']
    key = convert_keyname(username)
    red.hmset(key, mappings)


# redis에서 token attribute 가져오기
def get_token_from_redis(username: str = None):
    key = convert_keyname(username)
    val_from_redis = red.hgetall(key)
    values = [value for value in val_from_redis.values()]
    return values


# redis key값 변경
def convert_keyname(key: str) -> str:
    return f'{key}_id'
