import logging
import os
import sys

from config.settings import DEBUG

logger = logging.getLogger(__name__)


# logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def do_logging(log_info: str = None, msg: str = None, exc: Exception = None):
    loggers = ('debug', 'info', 'warning', 'error', 'critical')

    if log_info in loggers:
        logger_msg = f'{msg}'
        logger.__getattribute__(log_info)(logger_msg)
    if exc:
        logger.exception(exc)


def do_traceback(exc: Exception = None):
    if DEBUG is True:
        exc = exc
        exc_type, exc_obj, exc_tb = sys.exc_info()
        if exc_tb is not None:
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            # print(exc_type, fname, exc_tb.tb_lineno)
            result = f"type: {str(exc_type)}\nfile_name: {fname}\nline_number: {exc_tb.tb_lineno}"
            if exc:
                print(f'raised [{exc.__class__.__name__}]')
            else:
                print('-' * len(str(exc_type)))
            print(result)
            print('-' * len(str(exc_type)))
