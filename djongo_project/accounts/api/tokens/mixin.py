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
        payload = self.payload
        jti = payload[api_settings.JTI_CLAIM]
        username = str(payload[api_settings.USER_ID_CLAIM])
        values_set = get_token_from_redis(key=jti)
        # if not value_set - {username, 'True'}:
        if username in values_set and 'True' in values_set:
            do_traceback()
            raise BlacklistedTokenException({'Token': 'This token is already blacklisted'})

    def blacklist(self):
        payload = self.payload
        set_token_to_redis(
            jti=str(payload[api_settings.JTI_CLAIM]),
            username=str(payload[api_settings.USER_ID_CLAIM]),
            black='True'
        )

    @classmethod
    def for_user(cls, user: User) -> Token:
        token = super().for_user(user)
        return token
