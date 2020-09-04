from rest_framework.exceptions import ValidationError


class CustomValidationError(ValidationError):
    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail, code=code)
        details = {'detail': detail}
        self.detail = details


class DoNotRefreshTokenException(CustomValidationError):
    """did not refresh Token"""


class DoNotVerifyTokenException(CustomValidationError):
    """did not verify Token"""


class InvalidTokenException(CustomValidationError):
    """invlaid token"""


class WithoutTokenException(CustomValidationError):
    """without token"""


class BlacklistedTokenException(CustomValidationError):
    """token is blacklisted"""


class SerializerValidationException(CustomValidationError):
    """validation exception at validation"""


class RegistSerializerValidationException(CustomValidationError):
    """R"""


class RegistSerializerException(CustomValidationError):
    """invalid input value"""


class InvalidFields(CustomValidationError):
    """invalid field name"""


class AuthenticationFail(CustomValidationError):
    """A"""
