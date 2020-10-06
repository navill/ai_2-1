from typing import *

from django.http import Http404
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

from exceptions.api_exception import CustomValidationError


def custom_exception_handler(exc: Union[Exception, Type[Exception]], context: Dict) -> Response:
    response = exception_handler(exc, context)
    exception_name = exc.__class__.__name__

    if isinstance(exc, Http404):
        return response

    if isinstance(exc, ValidationError):
        exc = CustomValidationError(code='built-in_exception')

    if response is not None:
        if not getattr(exc, 'code', None):
            response.data['code'] = exc.default_code
        else:
            response.data['code'] = exc.code

        response.data['status_code'] = exc.status_code
        response.data['exception'] = exception_name

    return response
