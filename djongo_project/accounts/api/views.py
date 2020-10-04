import logging

from rest_framework import permissions, status
from rest_framework.views import APIView

from accounts.api.serializers import UserRegistSerializer, StaffUserRegistSerializer
from accounts.utils import PostMixin

logger = logging.getLogger('project_logger').getChild(__name__)


class RegisterView(PostMixin, APIView):
    """to regist user"""
    permission_classes = [permissions.AllowAny]
    serializer = UserRegistSerializer
    status = status.HTTP_201_CREATED


class StaffRegisterView(PostMixin, APIView):
    """to regist user"""
    permission_classes = [permissions.AllowAny]
    serializer = StaffUserRegistSerializer
    status = status.HTTP_201_CREATED
