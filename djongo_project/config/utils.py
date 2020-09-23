from asyncio.log import logger
from functools import wraps
from types import MethodType

from exceptions.common_exceptions import RetryLimitError

RETRIES_LIMIT = 3


def with_retry(retries_limit: int = RETRIES_LIMIT, allowed_exceptions=None):
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


class logging_with_level:
    """
    동작은 되지만 완전한 코드가 아님
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

    def __init__(self, level: str = 'info'):
        self.level = level

    def __call__(self, operation: callable):
        @wraps(operation)
        def wrapped(*args, **kwargs):
            logger_function = getattr(logger, self.level)
            logger_function(f'started execution of {operation.__qualname__}')
            return operation(*args, **kwargs)

        return wrapped

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return MethodType(self, instance)

# 디스크립터에 대한 개념이 이해되어야 할 듯
# https://stackoverflow.com/questions/9416947/python-class-based-decorator-with-parameters-that-can-decorate-a-method-or-a-fun
# class TestDeco:
#     def __init__(self, argument):
#         if hasattr('argument', '__call__'):
#             self.func = argument
#             self.argument = 'default foo baby'
#         else:
#             self.argument = argument
#
#     def __get__(self, obj, type=None):
#         return partial(self, obj)
#
#     def __call__(self, *args, **kwargs):
#         if not hasattr(self, 'func'):
#             self.func = args[0]
#             return self
#
#         self.func(*args, **kwargs)
