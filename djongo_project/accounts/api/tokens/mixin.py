from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token

from accounts.constants import User
from accounts.utils import set_payload_to_redis
from exceptions.api_exception import BlacklistedTokenException


class BlacklistTokenMixin:
    # check blacklist from result of redis
    def check_blacklist(self, payload: list):
        jti = self.payload[api_settings.JTI_CLAIM]

        if jti in payload and 'True' in payload:
            raise BlacklistedTokenException(self.error['token'])

    def blacklist(self):
        set_payload_to_redis(
            payload=self.payload,
            black='True'
        )

    @classmethod
    def for_user(cls, user: User) -> Token:
        token = super().for_user(user)
        return token
