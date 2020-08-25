import logging

from django.contrib.auth import get_user_model
from rest_framework import status, permissions

from config import settings

# common
User = get_user_model()
LOGGER = logging.getLogger(__name__)

# api.mixins
VALIDATION_TARGETS = ('username', 'email')

# api.views
PERMISSION = [permissions.IsAuthenticated]
if settings.DEBUG:
    PERMISSION = [permissions.AllowAny]

STATUS = {
    '200': status.HTTP_200_OK,
    '201': status.HTTP_201_CREATED,
    '400': status.HTTP_400_BAD_REQUEST,
}
