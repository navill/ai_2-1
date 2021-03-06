import logging

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt import authentication

from accounts.api.tokens.serializers import CustomTokenObtainSlidingSerializer, CustomTokenVerifySerializer, \
    CustomTokenRefreshSlidingSerializer, BlackListTokenSerializer
from accounts.constants import PERMISSION
from config.rest_conf.auth import UserAuthentication
from utilities.common.view_mixins import PostMixin

logger = logging.getLogger('project_logger').getChild(__name__)


class TokenBlackListView(PostMixin, APIView):
    # to logout
    authentication_classes = [UserAuthentication]
    permission_classes = PERMISSION
    required_attributes = {
        'serializer': BlackListTokenSerializer,
        'status': status.HTTP_200_OK
    }


class TokenObtainSlidingView(PostMixin, APIView):
    # to login
    permission_classes = [permissions.AllowAny]
    required_attributes = {
        'serializer': CustomTokenObtainSlidingSerializer,
        'status': status.HTTP_201_CREATED
    }


class TokenVerifyView(PostMixin, APIView):
    # to verify token + check blacklist
    authentication_classes = [UserAuthentication]
    permission_classes = PERMISSION
    required_attributes = {
        "serializer": CustomTokenVerifySerializer,
        "status": status.HTTP_200_OK
    }


class TokenRefreshView(PostMixin, APIView):
    # to refresh token
    authentication_classes = [UserAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    required_attributes = {
        "serializer": CustomTokenRefreshSlidingSerializer,
        "status": status.HTTP_201_CREATED
    }


class TestView(PostMixin, APIView):
    # to test
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, *args) -> Response:
        try:
            result = {
                'user': str(self.request.user),
                'user.role': self.request.user.role,
                'payload': self.request.auth.payload
            }
        except Exception:
            raise
        return Response({'result': result})
