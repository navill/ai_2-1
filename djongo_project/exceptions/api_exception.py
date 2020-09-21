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


class SerializerDefault:
    status_code = 400
    default_detail = 'raised validation error in serializer'
    default_code = 'invalid'


class TokenDefault:
    status_code = 403
    default_detail = 'raised authentication error in token serializer'
    default_code = 'unauthorized'


"""
Syntax
raise CustomException(detail='error message', code='error')
"""


class DoNotRefreshTokenException(TokenDefault, CustomValidationError):
    """did not refresh Token"""


class DoNotVerifyTokenException(TokenDefault, CustomValidationError):
    """did not verify Token"""


class InvalidTokenError(TokenDefault, CustomValidationError):
    """invlaid token"""


class WithoutTokenException(TokenDefault, CustomValidationError):
    """without token"""


class BlacklistedTokenException(TokenDefault, CustomValidationError):
    """token is blacklisted"""


class SerializerValidationException(SerializerDefault, CustomValidationError):
    """validation exception at validation"""


class RegistSerializerValidationException(SerializerDefault, CustomValidationError):
    """R"""


class RegistSerializerException(SerializerDefault, CustomValidationError):
    """invalid input value"""


class InvalidFields(SerializerDefault, CustomValidationError):
    """invalid field name"""


class UniqueValidationException(SerializerDefault, CustomValidationError):
    """not unique"""


class AuthenticationFail(TokenDefault, CustomValidationError):
    """Authentication Fail"""


class InvalidFilePathError(TokenDefault, CustomValidationError):
    """Invalid File path"""
