from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token

from accounts.constants import User
from accounts.exceptions.api_exception import BlacklistedTokenException
from accounts.utils import get_token_from_redis, set_token_to_redis
from config.utils_log import do_traceback


class BlacklistTokenMixin:
    def verify(self):
        super().verify()  # check expired time and token type -> raise TokenError
        self.check_blacklist()

    def check_blacklist(self):
        jti = self.payload[api_settings.JTI_CLAIM]
        token_from_redis = get_token_from_redis(self.payload)
        if token_from_redis == jti:
            do_traceback()
            raise BlacklistedTokenException({'Token': 'This token is already blacklisted'})

    def blacklist(self):
        set_token_to_redis(self.payload)

    @classmethod
    def for_user(cls, user: User) -> Token:
        token = super().for_user(user)
        return token
