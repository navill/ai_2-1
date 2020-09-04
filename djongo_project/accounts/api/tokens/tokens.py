from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token

from accounts.api.tokens.mixin import BlacklistTokenMixin
from accounts.exceptions.api_exception import InvalidTokenException
from accounts.utils import get_token_from_redis


class CustomSlidingToken(BlacklistTokenMixin, Token):
    token_type = 'sliding'
    lifetime = api_settings.SLIDING_TOKEN_LIFETIME
    error = {
        'token_error': 'Token has no id',
        'invalid_token': 'Invalid Token'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.token is None:
            self.set_exp(
                api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM,
                from_time=self.current_time,
                lifetime=api_settings.SLIDING_TOKEN_REFRESH_LIFETIME,
            )

    def verify(self):
        payload = self.payload

        # token 유효기간 체크
        self.check_exp()

        # token payload 체크
        if api_settings.JTI_CLAIM not in payload:
            raise TokenError(self.error['token_error'])

        # get token attributes in redis
        values_from_redis = get_token_from_redis(payload[api_settings.USER_ID_CLAIM])

        # token payload(in redis) 체크
        if payload[api_settings.JTI_CLAIM] not in values_from_redis:
            raise InvalidTokenException(self.error['invalid_token'])

        # token blacklisted 체크
        self.check_blacklist(values_from_redis)
