from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt import authentication

from accounts.api.tokens.serializers import CustomTokenObtainSlidingSerializer, CustomTokenVerifySerializer, \
    CustomTokenRefreshSlidingSerializer, BlackListTokenSerializer
from accounts.constants import PERMISSION, STATUS
from accounts.utils import do_post
# from config.settings import REDIS_OBJ
from config.rest_conf.auth import UserAuthentication


class TokenBlackListView(APIView):
    """to logout"""
    permission_classes = PERMISSION

    def post(self, request) -> Response:
        msg, stat = do_post(
            serializer=BlackListTokenSerializer,
            request=request,
            stat=STATUS['200']
        )
        return Response(msg, status=stat)


class TokenObtainSlidingView(APIView):
    # to login
    permission_classes = [permissions.AllowAny]

    def post(self, request) -> Response:
        msg, stat = do_post(
            serializer=CustomTokenObtainSlidingSerializer,
            request=request,
            stat=STATUS['201']
        )
        return Response(msg, stat)


class TokenVerifyView(APIView):
    # to verify token + check blacklist
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = PERMISSION

    def post(self, request) -> Response:
        msg, stat = do_post(
            serializer=CustomTokenVerifySerializer,
            request=request,
            stat=STATUS['200']
        )
        return Response(msg, stat)


class TokenRefreshView(APIView):
    # to refresh token
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = PERMISSION

    def post(self, request) -> Response:
        msg, stat = do_post(
            serializer=CustomTokenRefreshSlidingSerializer,
            request=request,
            stat=STATUS['201']
        )
        return Response(msg, stat)


class TestView(APIView):
    # authentication_classes = [authentication.JWTAuthentication]
    authentication_classes = [UserAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, *args) -> Response:
        result = {
            'user': str(self.request.user),
            'user.role': self.request.user.role,
            'payload': self.request.auth.payload
        }
        return Response({'result': result})
