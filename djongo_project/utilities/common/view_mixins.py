import logging
from collections import OrderedDict
from typing import *

from django.db.models.query import QuerySet
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.request import Request
from rest_framework.response import Response

from exceptions.api_exception import InvalidFields
from exceptions.common_exceptions import ClassMisconfiguration
from utilities.log_utils import create_log_msg

REQUIRED_ATTRIBUTES = ['required_attributes']
logger = logging.getLogger('project_logger').getChild(__name__)


class SerializerHandler:
    def __init__(self, data: Dict, serializer_obj, caller: str):
        self.data = data
        self.serializer_obj = serializer_obj
        self.caller = caller

    def __enter__(self):
        try:
            self.serializer_obj.is_valid(raise_exception=True)
        except Exception as e:
            message = str(e)
            raise InvalidFields(detail=message)

        return self.serializer_obj.validated_data

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb:
            print(exc_type, exc_val)


class BaseMixin:
    def initialize(self, attribute_list: List[str]) -> None:
        caller_class = type(self)

        try:
            self._set_common_attributes()
            for attribute_name in attribute_list:
                self._set_attributes(caller_class.__dict__[attribute_name])
        except KeyError as ke:
            key_name = str(ke)
            caller_name = caller_class.__name__
            raise ClassMisconfiguration(detail=f"{caller_name} do not have {key_name} attribute")

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = {
            'request': self.request,
            'view': self
        }
        return self.serializer(*args, **kwargs)

    def _set_common_attributes(self):
        setattr(self, 'caller', type(self).__name__)

    def _set_attributes(self, attribute_dict: dict) -> None:
        for name, attribute in attribute_dict.items():
            if attribute is not None:
                setattr(self, name, attribute)
            else:
                raise ClassMisconfiguration(detail=f"'{name}' attribute at {type(self).__name__} cannot be None!")


class PostMixin(BaseMixin):
    """
    필수 속성(required_attributes)
    - serializer: serializer
    - status: 정상 응답 상태
    동적으로 추가된 속성
    - caller: mixin 호출자
    - method: request의 method
    """

    def post(self, request: Request) -> Response:
        self.initialize(REQUIRED_ATTRIBUTES)
        # dynamic attributes
        caller = self.caller
        status = self.status
        method = request.method

        data = request.data
        serializer_obj = self.get_serializer(data=data)
        serializer_name = type(serializer_obj).__name__

        with SerializerHandler(data, serializer_obj, caller) as validated_data:
            if ('Regist' in serializer_name) and getattr(serializer_obj, 'create', None):
                serializer_obj.create(validated_data)
                logger.info(create_log_msg(method, caller, values=validated_data))

        response = Response(validated_data, status=status)
        logger.info(create_log_msg(method, caller))
        return response


class GetMixin(BaseMixin):
    """
    필수 속성(required_attributes)
    - serializer: serializer
    - status: 정상 응답 상태
    - queryset: 모델 쿼리셋
    동적으로 추가된 속성
    - caller: mixin 호출자
    - method: request의 method
    """

    def get(self, request: Request, *args, **kwargs) -> Response:
        self.initialize(REQUIRED_ATTRIBUTES)
        # dynamic attributes
        queryset = self.queryset
        caller = self.caller
        method = request.method

        if kwargs.get('pk', None):
            serialized_data = self._get_retrieve_data(**kwargs)
            logger.info(create_log_msg(method, caller, values=kwargs))
        else:
            serialized_data = self._get_list_data(queryset)
            logger.info(create_log_msg(method, caller))

        response = Response(serialized_data, status=self.status)
        return response

    def _get_list_data(self, queryset: QuerySet) -> OrderedDict:
        paginator = LimitPagination()
        page = paginator.paginate_queryset(queryset, self.request)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = paginator.get_paginated_response(serializer.data)
            return data

        serializer = self.get_serializer(queryset, many=True)
        return serializer.data

    def _get_retrieve_data(self, **kwargs) -> Dict:
        queryset = self.queryset
        obj = get_object_or_404(queryset, **kwargs)
        serializer = self.get_serializer(obj)
        return serializer.data


class LimitPagination(LimitOffsetPagination):
    def get_paginated_response(self, data: List) -> OrderedDict:
        return OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ])

