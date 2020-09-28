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


class SerializerDefaultError:
    status_code = 400
    default_detail = 'raised validation error in serializer'
    default_code = 'invalid'


class TokenDefaultError:
    status_code = 403
    default_detail = 'raised authentication error in token serializer'
    default_code = 'unauthorized'


"""
Syntax
raise CustomException(detail='error message', code='error')
"""


class DoNotRefreshTokenException(TokenDefaultError, CustomValidationError):
    """did not refresh Token"""


class DoNotVerifyTokenException(TokenDefaultError, CustomValidationError):
    """did not verify Token"""


class InvalidTokenError(TokenDefaultError, CustomValidationError):
    """invlaid token"""


class WithoutTokenException(TokenDefaultError, CustomValidationError):
    """without token"""


class BlacklistedTokenException(TokenDefaultError, CustomValidationError):
    """token is blacklisted"""


class SerializerValidationException(SerializerDefaultError, CustomValidationError):
    """validation exception at validation"""


class RegistSerializerValidationException(SerializerDefaultError, CustomValidationError):
    """R"""


class RegistSerializerException(SerializerDefaultError, CustomValidationError):
    """invalid input value"""


class InvalidFields(SerializerDefaultError, CustomValidationError):
    """invalid field name"""


class UniqueValidationException(SerializerDefaultError, CustomValidationError):
    """not unique"""


class AuthenticationFail(TokenDefaultError, CustomValidationError):
    """Authentication Fail"""


class InvalidFilePathError(TokenDefaultError, CustomValidationError):
    """Invalid File path"""


class WithoutPermissionError(SerializerDefaultError, CustomValidationError):
    """without permission"""
