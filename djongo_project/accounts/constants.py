from django.contrib.auth import get_user_model
from rest_framework import status, permissions

from config import settings

# common
User = get_user_model()
# api.mixins
VALIDATION_TARGETS = ('username', 'email')

# api.views
PERMISSION = [permissions.IsAuthenticated]
if settings.DEBUG:
    PERMISSION = [permissions.AllowAny]
