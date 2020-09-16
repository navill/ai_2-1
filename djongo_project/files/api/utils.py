import time

from cryptography.fernet import Fernet, InvalidToken

from key_file import *


class URLEnDecrypt:
    fern = Fernet(KEY['fernet'])

    @classmethod
    def encrypt(cls, text):
        enc_data = cls.fern.encrypt_at_time(text.encode('utf-8'), int(time.time()))
        return enc_data.decode('utf-8')

    @classmethod
    def decrypt(cls, text):
        try:
            dec_data = cls.fern.decrypt_at_time(text.encode('utf-8'), 3000, int(time.time()))
        except InvalidToken:
            raise InvalidToken('expired token')
        return dec_data.decode('utf-8')
