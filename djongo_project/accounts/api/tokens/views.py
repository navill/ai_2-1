from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt import authentication

from accounts.api.tokens.serializers import CustomTokenObtainSlidingSerializer, CustomTokenVerifySerializer, \
    CustomTokenRefreshSlidingSerializer, BlackListTokenSerializer
from accounts.constants import PERMISSION
from accounts.utils import do_post
from config.utils import logging


class TokenBlackListView(APIView):
    # to logout
    permission_classes = PERMISSION

    @logging
    def post(self, request) -> Response:
        msg = do_post(
            serializer=BlackListTokenSerializer,
            request=request
        )
        return Response(msg, status=status.HTTP_200_OK)


class TokenObtainSlidingView(APIView):
    # to login
    permission_classes = [permissions.AllowAny]

    @logging
    def post(self, request) -> Response:
        msg = do_post(
            serializer=CustomTokenObtainSlidingSerializer,
            request=request
        )
        return Response(msg, status=status.HTTP_201_CREATED)


class TokenVerifyView(APIView):
    # to verify token + check blacklist
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = PERMISSION

    @logging
    def post(self, request) -> Response:
        msg = do_post(
            serializer=CustomTokenVerifySerializer,
            request=request
        )
        return Response(msg, status=status.HTTP_200_OK)


class TokenRefreshView(APIView):
    # to refresh token
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = PERMISSION

    @logging
    def post(self, request) -> Response:
        msg = do_post(
            serializer=CustomTokenRefreshSlidingSerializer,
            request=request
        )
        return Response(msg, status=status.HTTP_201_CREATED)


class TestView(APIView):
    # to test
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @logging
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
