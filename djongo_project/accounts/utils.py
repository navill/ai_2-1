from rest_framework import status

from accounts.api.serializers import UserRegistSerializer
from accounts.constants import LOGGER


def do_logging(info: str = None, exc: Exception = None):
    LOGGER.info(info)
    if exc:
        LOGGER.exception(exc)


def _do_post(serializer=None, request=None, stat=None) -> tuple:
    data = request.data
    serializer = serializer(data=data)
    try:
        if serializer.is_valid():
            valid_data = serializer.validated_data
            if isinstance(serializer, UserRegistSerializer) and getattr(serializer, 'create', None):
                serializer.create(valid_data)
                valid_data = serializer.data
            return valid_data, stat
    except Exception as e:
        return {'status': str(e)}, status.HTTP_400_BAD_REQUEST
