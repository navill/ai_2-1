from asyncio.log import logger
from functools import wraps
from types import MethodType

from exceptions.common_exceptions import RetryLimitError

RETRIES_LIMIT = 3


def with_retry(retries_limit=RETRIES_LIMIT, allowed_exceptions=None):
    allowed_exceptions = allowed_exceptions

    def retry(operation):
        @wraps(operation)
        def wrapped(*args, **kwargs):
            last_raised = None
            for _ in range(retries_limit):
                try:
                    return operation(*args, **kwargs)
                except allowed_exceptions as e:
                    last_raised = RetryLimitError(detail=e.args[0])
            raise last_raised

        return wrapped

    return retry


class logging:
    def __init__(self, function):
        self.function = function
        wraps(self.function)(self)

    def __call__(self, *args, **kwargs):
        logger.warning(f'started execution of {self.function.__qualname__}')
        return self.function(*args, **kwargs)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.__class__(MethodType(self.function, instance))
