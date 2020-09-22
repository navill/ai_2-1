import mimetypes
import os
import urllib

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
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
from config.utils import logging
from exceptions.api_exception import InvalidFilePathError
from exceptions.common_exceptions import InvalidValueError, ObjectDoesNotExistError
from files.api.serializers import FileManageSerializer
from files.api.utils import DecryptHandler
from files.models import CommonFile

if settings.DEBUG:
    permissions = [AllowAny]
else:
    permissions = [UserAuthentication]


class FileView(ListModelMixin, RetrieveModelMixin, GenericAPIView):
    queryset = CommonFile.objects.all().order_by('-created_at')
    serializer_class = FileManageSerializer
    permission_classes = permissions
    parser_classes = (MultiPartParser, FormParser)

    @logging
    def get(self, request, *args, **kwargs):
        if kwargs.get('pk', None):
            return self.retrieve(request, *args, **kwargs)
        else:
            return self.list(request, *args, **kwargs)


class FileUploadView(CreateModelMixin, GenericAPIView):
    serializer_class = FileManageSerializer
    permission_classes = permissions
    parser_classes = (MultiPartParser, FormParser)

    @logging
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

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


@api_view(['GET'])
@permission_classes(permissions)
@logging
def download_view(request: Request, path: str) -> HttpResponseBase:
    file_id = get_file_id(path)
    file_obj = get_file_object(file_id=file_id)

    if file_obj.is_owner(request.user):
        try:
            handler = file_obj.file.open()
        except Exception as e:
            raise InvalidFilePathError(detail='Invalid file path') from e

        response = create_file_response(handler)
        return response
    return Response('Do not have permission to access this link', status=status.HTTP_401_UNAUTHORIZED)  # for drf


def get_file_id(path: str) -> int:
    handler = DecryptHandler(path)
    file_id = handler.decrypt()
    try:
        return int(file_id)
    except ValueError:
        raise


def get_file_object(file_id: int):
    try:
        return CommonFile.objects.get(id=file_id)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExistError(detail='Does not find file')


def create_file_response(handler: FieldFile) -> FileResponse:
    non_ascii_filename = os.path.basename(handler.name)
    filename = convert_name_to_ascii(non_ascii_filename)

    response = FileResponse(handler, content_type=mimetypes.guess_type(filename)[0])
    response['Content-Length'] = handler.size
    response['Content-Disposition'] = 'attachment; filename=' + filename
    return response


def convert_name_to_ascii(filename: str) -> str:
    try:
        return urllib.parse.quote(string=filename)
    except [UnicodeEncodeError, TypeError]:
        raise InvalidValueError(detail='Can not quote filename')
