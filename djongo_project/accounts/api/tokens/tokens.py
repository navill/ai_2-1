import logging

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token

from accounts.api.tokens.mixin import BlacklistTokenMixin
from accounts.utils import get_payload_from_redis
from exceptions.api_exception import InvalidTokenError

logger = logging.getLogger('project_logger').getChild(__name__)


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
            logger.warning('invalid token')
            raise InvalidTokenError(detail=self.error['invalid_token'])

        if self.token is None:
            self.set_exp(
                api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM,
                from_time=self.current_time,
                lifetime=api_settings.SLIDING_TOKEN_REFRESH_LIFETIME,
            )

    def verify(self):
        token_payload = self.payload
        username = token_payload[api_settings.USER_ID_CLAIM]
        payload_from_redis = get_payload_from_redis(username)

        self.check_exp()
        self._check_jti()
        self._compare_jti_with(payload_from_redis)
        self.check_blacklist(payload_from_redis)

    def _check_jti(self):
        jti = api_settings.JTI_CLAIM

        if jti not in self.payload:
            logger.warning('token error')
            raise InvalidTokenError(detail=self.error['token_error'])

    def _compare_jti_with(self, saved_payload):
        if self.payload[api_settings.JTI_CLAIM] not in saved_payload:
            logger.warning('not match token with saved payload')
            raise InvalidTokenError(detail=self.error['invalid_token'])
