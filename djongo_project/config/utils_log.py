import logging

logger = logging.getLogger(__name__)
# logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def do_logging(log_info: str = None, msg: str = None, exc: Exception = None):
    loggers = ('debug', 'info', 'warning', 'error', 'critical')

    if log_info in loggers:
        logger_msg = f'{msg}'
        logger.__getattribute__(log_info)(logger_msg)
    if exc:
        logger.exception(exc)
