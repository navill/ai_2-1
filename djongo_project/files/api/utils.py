import time

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

from exceptions.api_exception import InvalidTokenError
from key_file import *


class FernetHandler:
    def __init__(self, text: str):
        self.fern = Fernet(KEY['fernet'])
        self.url = text.encode()
        self.current_time = int(time.time())

    def _decode_url(self, url: bytes) -> str:
        return url.decode()  # exception을 잡아야할까?


class EncryptHandler(FernetHandler):
    def encrypt_to_str(self) -> str:
        byte_url = self.fern.encrypt_at_time(self.url, self.current_time)
        return self._decode_url(byte_url)


class DecryptHandler(FernetHandler):
    def decrypt_to_str(self) -> str:
        if settings.DEBUG:
            to_expire = 3000
        else:
            to_expire = 30

        try:
            byte_url = self.fern.decrypt_at_time(self.url, to_expire, self.current_time)
        except InvalidToken as it:
            raise InvalidTokenError(detail='Invalid url token') from it

        return self._decode_url(byte_url)
