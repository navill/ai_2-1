from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.api.serializers import UserRegistSerializer
from accounts.constants import STATUS
from accounts.utils import _do_post


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
