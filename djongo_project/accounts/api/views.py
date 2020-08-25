from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt import authentication

from accounts.api.mixins import BlackMixin
from accounts.api.serializers import UserRegistSerializer
from accounts.api.tokens.serializers import CustomTokenObtainSlidingSerializer, CustomTokenRefreshSlidingSerializer, \
    CustomTokenVerifySerializer
from accounts.constants import PERMISSION, STATUS
from accounts.exceptions.api_exception import WithoutTokenException, InvalidTokenException
from accounts.utils import _do_post


class TokenBlackListView(BlackMixin, APIView):
    """to logout"""
    permission_classes = PERMISSION

    def post(self, request):
        msg, stat = 'ok', STATUS['200']
        try:
            # mixin? function? class?
            token = self.get_sliding_token(request)
            self.regist_blacklist(token)

        except WithoutTokenException as wte:
            msg, stat = wte, STATUS['400']
        except InvalidTokenException as ite:
            msg, stat = ite, STATUS['400']

        return Response({'status': msg}, status=stat)


class TokenObtainSlidingView(APIView):
    # to login
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        msg, stat = _do_post(
            serializer=CustomTokenObtainSlidingSerializer,
            request=request,
            stat=STATUS['201']
        )
        return Response(msg, stat)


class TokenVerifyView(APIView):
    # to verify token + check blacklist
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = PERMISSION

    def post(self, request):
        msg, stat = _do_post(
            serializer=CustomTokenVerifySerializer,
            request=request,
            stat=STATUS['200']
        )
        return Response(msg, stat)


class TokenRefreshView(APIView):
    # to refresh token
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = PERMISSION

    def post(self, request):
        msg, stat = _do_post(
            serializer=CustomTokenRefreshSlidingSerializer,
            request=request,
            stat=STATUS['201']
        )
        return Response(msg, stat)


class RegisterView(APIView):
    """to regist user"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        msg, stat = _do_post(
            serializer=UserRegistSerializer,
            request=request,
            stat=STATUS['201']
        )
        return Response(msg, stat)

# class AuthTestView(APIView):
#     # for test
#     authentication_classes = [authentication.JWTAuthentication]
#     permission_classes = PERMISSION
# 
#     def post(self, request):
#         return _do_post(AuthTestSerializer, request)
