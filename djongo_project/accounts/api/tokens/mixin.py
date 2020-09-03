from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token

from accounts.constants import User
from accounts.exceptions.api_exception import BlacklistedTokenException
from accounts.utils import get_token_from_redis, set_token_to_redis
from config.utils_log import do_traceback


class BlacklistTokenMixin:
    def check_blacklist(self, values_from_redis):
        jti = self.payload[api_settings.JTI_CLAIM]
        # print('check_redis1')
        # values = get_token_from_redis(username=username)
        if jti in values_from_redis and 'True' in values_from_redis:
            do_traceback()
            raise BlacklistedTokenException({'Token': 'This token is already blacklisted'})

    def blacklist(self):
        set_token_to_redis(
            payload=self.payload,
            black=True
        )

    @classmethod
    def for_user(cls, user: User) -> Token:
        token = super().for_user(user)
        return token
