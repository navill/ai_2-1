from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.utils import datetime_from_epoch

from accounts.constants import User
from accounts.exceptions.api_exception import BlacklistedTokenException
from accounts.models import CustomBlack, CustomOutstanding
from config.utils_log import do_logging


class CustomSlidingToken(Token):
    token_type = 'sliding'
    lifetime = api_settings.SLIDING_TOKEN_LIFETIME

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.token is None:
            # Set sliding refresh expiration claim if new token
            self.set_exp(
                api_settings.SLIDING_TOKEN_REFRESH_EXP_CLAIM,
                from_time=self.current_time,
                lifetime=api_settings.SLIDING_TOKEN_REFRESH_LIFETIME,
            )

    def verify(self, *args, **kwargs):
        self.check_blacklist()
        super().verify()  # check expired time and token type

    def check_blacklist(self):
        jti = self.payload[api_settings.JTI_CLAIM]

        if CustomBlack.objects.filter(token__jti=jti).exists():
            exc = BlacklistedTokenException('This token is blacklisted')
            do_logging('warning', 'WARINING| token is blacklisted', exc=exc)
            raise exc

    def blacklist(self):
        jti = self.payload[api_settings.JTI_CLAIM]
        exp = self.payload['exp']

        token, _ = CustomOutstanding.objects.get_or_create(
            jti=jti,
            defaults={
                'token': str(self),
                'expires_at': datetime_from_epoch(exp),
            },
        )

        return CustomBlack.objects.get_or_create(token=token)

    @classmethod
    def for_user(cls, user: User) -> Token:
        token = super().for_user(user)

        jti = token[api_settings.JTI_CLAIM]
        exp = token['exp']

        CustomOutstanding.objects.create(
            user=user,
            jti=jti,
            token=str(token),
            created_at=token.current_time,
            expires_at=datetime_from_epoch(exp),
        )

        return token
