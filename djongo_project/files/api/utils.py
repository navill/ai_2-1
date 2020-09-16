import time

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

from key_file import *

if settings.DEBUG:
    exp_time = 3000
else:
    exp_time = 30


class URLEnDecrypt:
    fern = Fernet(KEY['fernet'])

    @classmethod
    def encrypt(cls, text: str) -> str:
        enc_data = cls.fern.encrypt_at_time(text.encode('utf-8'), int(time.time()))
        return enc_data.decode('utf-8')

    @classmethod
    def decrypt(cls, text: str) -> str:
        try:
            dec_data = cls.fern.decrypt_at_time(text.encode('utf-8'), exp_time, int(time.time()))
        except InvalidToken:
            raise InvalidToken('expired token')
        return dec_data.decode('utf-8')
