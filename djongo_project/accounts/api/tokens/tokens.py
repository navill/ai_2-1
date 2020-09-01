from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token

from accounts.api.tokens.mixin import BlacklistTokenMixin


class CustomSlidingToken(BlacklistTokenMixin, Token):
    token_type = 'sliding'
    lifetime = api_settings.SLIDING_TOKEN_LIFETIME

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.token is None:
            self.set_exp(
                api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM,
                from_time=self.current_time,
                lifetime=api_settings.SLIDING_TOKEN_REFRESH_LIFETIME,
            )
