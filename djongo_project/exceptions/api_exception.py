from rest_framework import status
from rest_framework.exceptions import APIException


class CustomValidationError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'
    default_code = 'error'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        self.detail = detail
        self.code = code


class SerializerDefaultMixin:
    status_code = 400
    default_detail = 'raised validation error in serializer'
    default_code = 'invalid'


class TokenDefaultMixin:
    status_code = 403
    default_detail = 'raised authentication error in token serializer'
    default_code = 'unauthorized'


class DoNotRefreshTokenException(TokenDefaultMixin, CustomValidationError):
    """did not refresh Token"""


class DoNotVerifyTokenException(TokenDefaultMixin, CustomValidationError):
    """did not verify Token"""


class InvalidTokenException(TokenDefaultMixin, CustomValidationError):
    """invlaid token"""


class WithoutTokenException(TokenDefaultMixin, CustomValidationError):
    """without token"""


class BlacklistedTokenException(TokenDefaultMixin, CustomValidationError):
    """token is blacklisted"""


class SerializerValidationException(SerializerDefaultMixin, CustomValidationError):
    """validation exception at validation"""


class RegistSerializerValidationException(SerializerDefaultMixin, CustomValidationError):
    """R"""


class RegistSerializerException(SerializerDefaultMixin, CustomValidationError):
    """invalid input value"""


class InvalidFields(SerializerDefaultMixin, CustomValidationError):
    """invalid field name"""


class UniqueValidationException(SerializerDefaultMixin, CustomValidationError):
    """not unique"""


class AuthenticationFail(TokenDefaultMixin, CustomValidationError):
    """A"""
