from typing import *


def create_log_msg(method=None, caller=None, values: Union[Text, List, Tuple, Dict] = None,
                   message: str = None):
    msg = [f'[{method}][excuted {caller}]']
    if values:
        msg.append(f"[values:{values}]")
    if message:
        msg.append(f"[message:{message}")
    return ''.join(msg)


