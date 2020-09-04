from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token

from accounts.constants import User
from accounts.utils import set_token_to_redis
from config.utils_log import do_traceback


class BlacklistTokenMixin:
    # check blacklist from result of redis
    def check_blacklist(self, values_from_redis: list):
        jti = self.payload[api_settings.JTI_CLAIM]

        # valid jti 및 blacklisted 여부 체크
        if jti in values_from_redis and 'True' in values_from_redis:
            do_traceback()
            raise TokenError(self.error['token'])

    # set blacklist to redis
    def blacklist(self):
        set_token_to_redis(
            payload=self.payload,
            black=True
        )

    @classmethod
    def for_user(cls, user: User) -> Token:
        token = super().for_user(user)
        return token
