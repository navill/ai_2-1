import logging
import mimetypes
import os
import urllib

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.fields.files import FieldFile
from django.db.models.query import QuerySet
from django.http import FileResponse
from django.http.response import HttpResponseBase
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import *
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from config.rest_conf.auth import UserAuthentication
from exceptions.api_exception import InvalidFilePathError
from exceptions.common_exceptions import InvalidValueError, ObjectDoesNotExistError
from files.api.serializers import FileManageSerializer
from utilities.common_utils import GetMixin
from utilities.file_utils import DecryptHandler
from files.models import CommonFile

logger = logging.getLogger('project_logger').getChild(__name__)

if settings.DEBUG:
    permissions = [AllowAny]
else:
    permissions = [IsAuthenticated]


class FileViewTest(ListModelMixin, RetrieveModelMixin, GenericAPIView):
    queryset = CommonFile.objects.all().order_by('-created_at')
    serializer_class = FileManageSerializer
    permission_classes = permissions
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request: Request, *args, **kwargs) -> Response:
        if kwargs.get('pk', None):
            response = self.retrieve(request, *args, **kwargs)
        else:
            response = self.list(request, *args, **kwargs)
            logger.info('[GET] file list')

        return response

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)


class FileView(GetMixin, APIView):
    authentication_classes = [UserAuthentication]
    permission_classes = [AllowAny]

    required_attributes = {
        'serializer': FileManageSerializer,
        'status': status.HTTP_200_OK,
        'queryset': CommonFile.objects.all().order_by('-created_at')
    }


class FileUploadView(CreateModelMixin, GenericAPIView):
    serializer_class = FileManageSerializer
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs) -> Response:
        response = self.create(request, *args, **kwargs)
        logger.info('[POST] upload file')
        return response

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     return queryset.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes(permissions)
def download_view(request: Request, path: str) -> HttpResponseBase:
    file_id = get_file_id(path)
    file_obj = get_file_object(file_id=file_id)
    fieldfile = file_obj.file

    if file_obj.is_owner(request.user):
        try:
            handler = fieldfile.open()
        except Exception as e:
            logger.warning(f"invalid file path({file_obj})")
            raise InvalidFilePathError(detail='Invalid file path') from e

        file_name = get_file_name(handler)
        response = response_with_file(handler, file_name)

        logger.info(f'[GET] download file-{file_name}')
        return response

    logger.warning(f"try to access download link({fieldfile.name}) without permission")
    return Response('Do not have permission to access this link', status=status.HTTP_401_UNAUTHORIZED)  # for drf


def get_file_id(path: str) -> int:
    handler = DecryptHandler(path)
    file_id = handler.decrypt()
    try:
        return int(file_id)
    except ValueError:
        raise


def get_file_object(file_id: int) -> CommonFile:
    try:
        return CommonFile.objects.get(id=file_id)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExistError(detail='file not found')


def get_file_name(handler: FieldFile) -> str:
    non_ascii_filename = os.path.basename(handler.name)
    filename = convert_name_to_ascii(non_ascii_filename)
    return filename


def response_with_file(handler: FieldFile, filename: str) -> FileResponse:
    response = FileResponse(handler, content_type=mimetypes.guess_type(filename)[0])
    response['Content-Length'] = handler.size
    response['Content-Disposition'] = 'attachment; filename=' + filename
    return response


def convert_name_to_ascii(filename: str) -> str:
    try:
        return urllib.parse.quote(string=filename)
    except [UnicodeEncodeError, TypeError]:
        raise InvalidValueError(detail='Can not quote filename')
