from functools import wraps

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
