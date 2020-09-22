from asyncio.log import logger
from functools import wraps
from types import MethodType

from exceptions.common_exceptions import RetryLimitError

RETRIES_LIMIT = 3


def with_retry(retries_limit: int = RETRIES_LIMIT, allowed_exceptions: Exception = None):
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


class logging_with_arg:
    """
    description:
    logging 동작에 사용될 메서드 이름을 인자로 전달하여 logger 기록

    usage : 함수 데코레이터
    @logging_with_arg('warning')
    def func():
        ...

    usage : 메서드 데코레이터
    class Klass:
        @logging_with_arg('warnging')
        def func():
            ...
    """

    def __init__(self, logger_name: str):
        self.logger_name = logger_name

    def __call__(self, operation: callable):
        @wraps(operation)
        def wrapped(*args, **kwargs):
            logger_function = getattr(logger, self.logger_name)
            logger_function(f'started execution of {operation.__qualname__}')
            return operation(*args, **kwargs)

        return wrapped

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance
