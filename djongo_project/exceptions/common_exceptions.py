from exceptions.api_exception import CustomValidationError


class DefaultAttributes:
    status_code = 400
    default_detail = 'default'
    default_code = 'default_error'


class ObjectExistError(DefaultAttributes, CustomValidationError):
    """object"""


class ObjectDoesNotExistError(DefaultAttributes, CustomValidationError):
    """object"""


class InvalidValueError(DefaultAttributes, CustomValidationError):
    """value error"""


class RedisConnectionError(DefaultAttributes, CustomValidationError):
    """redis connection fail"""


class RetryLimitError(DefaultAttributes, CustomValidationError):
    """retry limit error"""
    status = 500
    default_detail = 'retry_connection'
    default_code = 'connection_error'
