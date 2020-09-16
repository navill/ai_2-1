import mimetypes
import os
import urllib

from bson import binary
from django.conf import settings
from django.db.models import QuerySet
from django.db.models.fields.files import FieldFile
from django.http import FileResponse
from django.http.response import HttpResponseBase
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import *
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from config.rest_conf.auth import UserAuthentication
from files.api.serializers import FileManageSerializer
from files.api.utils import URLEnDecrypt
from files.models import CommonFile


class FileView(ListModelMixin, RetrieveModelMixin, GenericAPIView):
    queryset = CommonFile.objects.all().order_by('-created_at')
    serializer_class = FileManageSerializer
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk', None):
            return self.retrieve(request, *args, **kwargs)
        else:
            return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        file_serializer = FileManageSerializer(data=request.data, context={'request': request})
        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        assert self.queryset is not None, (
                "'%s' should either include a `queryset` attribute, "
                "or override the `get_queryset()` method."
                % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            queryset = queryset.filter(user=self.request.user)
        return queryset


if settings.DEBUG:
    permissions = [AllowAny]
else:
    permissions = [UserAuthentication]


@api_view(['GET'])
@permission_classes(permissions)
def download(request: Request, path: binary) -> HttpResponseBase:
    file_id = get_file_id(path)
    file_obj = CommonFile.objects.get(id=file_id)

    if file_obj.is_owner(request.user):
        try:
            handler = file_obj.file.open()
            response = create_file_response(handler)
        except Exception:
            raise FileNotFoundError('Invalid file path')
        return response
    else:
        return Response('Do not have permission to access this link', status=status.HTTP_401_UNAUTHORIZED)  # for drf


def get_file_id(path: binary) -> str:
    decrypted_url = URLEnDecrypt.decrypt(path)
    return urllib.parse.unquote(decrypted_url)


def create_file_response(handler: FieldFile) -> FileResponse:
    file_name = os.path.basename(handler.name)
    mime_type, _ = mimetypes.guess_type(file_name)
    quoted_name = urllib.parse.quote(file_name.encode('utf-8'))
    # 자동으로 FieldFile.close() 실행 ref: https://docs.djangoproject.com/en/3.1/ref/request-response/#fileresponse-objects
    response = FileResponse(handler, content_type=mime_type)
    response['Content-Length'] = handler.size
    response['Content-Disposition'] = 'attachment; filename=' + quoted_name
    return response
