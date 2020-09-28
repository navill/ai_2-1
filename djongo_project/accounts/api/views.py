import logging

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.api.serializers import UserRegistSerializer, StaffUserRegistSerializer
from accounts.utils import do_post

logger = logging.getLogger('project_logger').getChild(__name__)


class RegisterView(APIView):
    """to regist user"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        msg = do_post(
            serializer=UserRegistSerializer,
            request=request
        )
        return Response(msg, status=status.HTTP_201_CREATED)


class StaffRegisterView(APIView):
    """to regist user"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        msg = do_post(
            serializer=StaffUserRegistSerializer,
            request=request,
        )
        return Response(msg, status=status.HTTP_201_CREATED)
