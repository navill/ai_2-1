import redis
from rest_framework_simplejwt.settings import api_settings

from accounts.constants import STATUS
from config.settings import REDIS_CONN_POOL_1
from config.utils_log import do_traceback

red = redis.StrictRedis(connection_pool=REDIS_CONN_POOL_1)


def do_post(serializer=None, request=None, stat=None) -> tuple:
    serialized = serializer(data=request.data)
    try:
        if serialized.is_valid(raise_exception=True):  # if is_valid is false, raise serializers.ValidationError
            msg = serialized.validated_data
            # if isinstance(serialized, UserRegistSerializer) and getattr(serialized, 'create', None):
            if serialized.__class__ == 'UserRegistSerializer' and getattr(serialized, 'create', None):
                serialized.create(serialized.validated_data)
                # msg = serialized.validated_data  # validated_data = to_internal_value() -> is_valid()
                msg = serialized.data  # data = to_representation()
            return msg, stat
    except Exception as e:
        do_traceback()
        return {'msg': str(e)}, STATUS['400']


def set_token_to_redis(payload: dict):
    red.set(name=str(payload[api_settings.USER_ID_CLAIM]),
            value=str(payload[api_settings.JTI_CLAIM]))
    # 5분 이내: blacklisted token
    # 5분 이후: expired token


def get_token_from_redis(payload: dict) -> str:
    jti = red.get(name=payload[api_settings.USER_ID_CLAIM])
    return str(jti) or ''


def del_token_to_redis(payload: dict):
    red.delete(name=payload[api_settings.USER_ID_CLAIM])
