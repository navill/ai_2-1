import time

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

from exceptions.api_exception import InvalidTokenError
from key_file import *


class URLHandler:
    fern = Fernet(KEY['fernet'])

    def __init__(self, text: str):
        self.url = text.encode()
        self.current_time = int(time.time())

        if settings.DEBUG:
            exp_time = 3000
        else:
            exp_time = 30
        self.expire_time = exp_time

    def encrypt_to_str(self) -> str:
        byte_url = self.fern.encrypt_at_time(self.url, self.current_time)
        return self.decode_url(byte_url)

    def decrypt_to_str(self) -> str:
        try:
            byte_url = self.fern.decrypt_at_time(self.url, self.expire_time, self.current_time)
        except InvalidToken as it:
            raise InvalidTokenError(detail='Invalid url token') from it
        return self.decode_url(byte_url)

    def decode_url(self, url: bytes) -> str:
        return url.decode()
