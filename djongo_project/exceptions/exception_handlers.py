from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

from exceptions.api_exception import CustomValidationError
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc: Exception, context: dict) -> Response:
    response = exception_handler(exc, context)

    if isinstance(exc, ValidationError):
        # logger.warning('raised built-in exception')
        exc = CustomValidationError(code='built-in_exception')

    if response is not None:
        if not getattr(exc, 'code', None):
            response.data['code'] = exc.default_code
        else:
            response.data['code'] = exc.code

        response.data['status_code'] = exc.status_code
        response.data['exception'] = exc.__class__.__name__
        logger.warning(exc.detail)
    return response
