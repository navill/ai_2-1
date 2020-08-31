class DoNotRefreshTokenException(Exception):
    """did not refresh Token"""


class DoNotVerifyTokenException(Exception):
    """did not verify Token"""


class InvalidTokenException(Exception):
    """invlaid token"""


class WithoutTokenException(Exception):
    """without token"""


class BlacklistedTokenException(Exception):
    """token is blacklisted"""


class SerializerValidationException(Exception):
    """validation exception at validation"""


class PostException(Exception):
    pass
