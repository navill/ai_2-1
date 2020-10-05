def create_log_msg(klass=None, caller=None, values=None, message=None):
    method = get_method(klass)

    msg = [f'[{method}][excuted {caller}]']
    if values:
        msg.append(f"[values:{values}]")
    if message:
        msg.append(f"[message:{message}")
    return ''.join(msg)


def get_method(klass):
    if hasattr(klass, 'queryset'):
        return 'GET'
    else:
        return 'POST'
