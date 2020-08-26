from rest_framework import status

from accounts.api.serializers import UserRegistSerializer
from accounts.constants import LOGGER, STATUS


def do_logging(info: str = None, exc: Exception = None):
    LOGGER.info(info)
    if exc:
        LOGGER.exception(exc)


def _do_post(serializer=None, request=None, stat=None) -> tuple:
    serialized = serializer(data=request.data)
    try:
        if serialized.is_valid(raise_exception=True):  # if is_valid is false, raise serializers.ValidationError
            msg = serialized.validated_data
            if isinstance(serialized, UserRegistSerializer) and getattr(serialized, 'create', None):
                serialized.create(serialized.validated_data)
                # msg = serialized.validated_data  # validated_data = to_internal_value() -> is_valid()
                msg = serialized.data  # data = to_representation()
            return msg, stat
    except Exception as e:
        return {'status': str(e)}, STATUS['400']
