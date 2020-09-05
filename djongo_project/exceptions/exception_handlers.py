from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler

from exceptions.api_exception import CustomValidationError


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, ValidationError):
        exc = CustomValidationError(code='built-in_exception')

    if response is not None:
        response.data['code'] = exc.code
        response.data['status_code'] = exc.status_code
        response.data['exception'] = exc.__class__.__name__
    return response
