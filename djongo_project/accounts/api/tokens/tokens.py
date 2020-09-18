from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token

from accounts.api.tokens.mixin import BlacklistTokenMixin
from accounts.utils import get_payload_from_redis
from exceptions.api_exception import InvalidTokenError


class CustomSlidingToken(BlacklistTokenMixin, Token):
    token_type = 'sliding'
    lifetime = api_settings.SLIDING_TOKEN_LIFETIME
    error = {
        'token': 'This token is already blacklisted',
        'token_error': 'Token has no id',
        'invalid_token': 'Invalid Token'
    }

    def __init__(self, *args, **kwargs):
        try:
            super().__init__(*args, **kwargs)
        except TokenError:
            raise InvalidTokenError(detail=self.error['invalid_token'])

        if self.token is None:
            self.set_exp(
                api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM,
                from_time=self.current_time,
                lifetime=api_settings.SLIDING_TOKEN_REFRESH_LIFETIME,
            )

    def verify(self):
        token_payload = self.payload
        # token 유효기간 체크
        self.check_exp()

        # token payload 체크
        if api_settings.JTI_CLAIM not in token_payload:
            raise InvalidTokenError(detail=self.error['token_error'])

        redis_payload = get_payload_from_redis(token_payload[api_settings.USER_ID_CLAIM])

        # token payload(in redis) 체크
        if token_payload[api_settings.JTI_CLAIM] not in redis_payload:
            raise InvalidTokenError(detail=self.error['invalid_token'])

        self.check_blacklist(redis_payload)
