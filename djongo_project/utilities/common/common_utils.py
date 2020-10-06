import logging
from functools import wraps
from typing import *

from redis.exceptions import ConnectionError

from exceptions.common_exceptions import RetryLimitError

RETRIES_LIMIT = 3
REQUIRED_ATTRIBUTES = ['required_attributes']

logger = logging.getLogger('project_logger').getChild(__name__)


def with_retry(retries_limit: int = RETRIES_LIMIT, allowed_exceptions: Type[Exception] = None):
    allowed_exceptions = allowed_exceptions or (ConnectionError,)

    def retry(operation):
        @wraps(operation)
        def wrapped(*args, **kwargs):
            logger = logging.getLogger('project_logger').getChild(__name__)
            last_raised = None
            for _ in range(retries_limit):
                try:
                    return operation(*args, **kwargs)
                except allowed_exceptions as e:
                    error_msg = e.args[0]
                    last_raised = RetryLimitError(detail=error_msg)
            logger.warning('not connect redis server')
            raise last_raised

        return wrapped

    return retry


def get_method(request):
    return request.method
