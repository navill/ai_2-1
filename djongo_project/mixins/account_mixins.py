import logging
from typing import *

from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token

from accounts.constants import User
from utilities.account_utils import set_payload_to_redis
from exceptions.api_exception import BlacklistedTokenException

logger = logging.getLogger('project_logger').getChild(__name__)


class BlacklistTokenMixin:
    def check_blacklist(self, payload: list) -> None:
        jti = self.payload[api_settings.JTI_CLAIM]

        if jti in payload and 'True' in payload:
            logger.warning('already blacklist token')
            raise BlacklistedTokenException(self.error['token'])

    def blacklist(self) -> None:
        set_payload_to_redis(
            payload=self.payload,
            black='True'
        )
        logger.info('blacklist token')

    @classmethod
    def for_user(cls, user: User) -> Type[Token]:
        token = super().for_user(user)
        return token
