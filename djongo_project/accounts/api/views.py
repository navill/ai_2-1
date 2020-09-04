from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.api.serializers import UserRegistSerializer, StaffUserRegistSerializer
from accounts.constants import STATUS
from accounts.utils import do_post


class RegisterView(APIView):
    """to regist user"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        msg, stat = do_post(
            serializer=UserRegistSerializer,
            request=request,
            stat=STATUS['201']
        )
        return Response(msg, stat)


class StaffRegisterView(APIView):
    """to regist user"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        msg, stat = do_post(
            serializer=StaffUserRegistSerializer,
            request=request,
            stat=STATUS['201']
        )
        return Response(msg, stat)
