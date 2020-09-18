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
