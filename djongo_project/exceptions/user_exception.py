from rest_framework.exceptions import APIException, ValidationError


class UniqueConstrainUserNameAPIException(APIException):
    """duplicated id"""


class NotMatchPasswordAPIException(ValidationError):
    """do not match password"""


class NotEnoughPasswordLengthAPIException(ValidationError):
    """invlaid token"""
