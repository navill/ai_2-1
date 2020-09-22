from exceptions.api_exception import CustomValidationError


class DefaultError:
    status_code = 400
    default_detail = 'default'
    default_code = 'default_error'


class ServerDefaultError:
    status_code = 500
    default_detail = 'server_error'
    default_code = 'connection_error'


class ObjectExistError(DefaultError, CustomValidationError):
    """object"""


class ObjectDoesNotExistError(DefaultError, CustomValidationError):
    """object"""


class InvalidValueError(DefaultError, CustomValidationError):
    """value error"""


class RedisConnectionError(ServerDefaultError, CustomValidationError):
    """redis connection fail"""


class RetryLimitError(ServerDefaultError, CustomValidationError):
    """retry limit error"""
    status_code = 500
    default_detail = 'retry_connection'
