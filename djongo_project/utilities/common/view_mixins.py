import logging
from collections import OrderedDict
from typing import *

# from rest_framework.filters import SearchFilter
from django.db.models.query import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.settings import api_settings

from exceptions.api_exception import InvalidFields
from exceptions.common_exceptions import ClassMisconfiguration
from utilities.log_utils import create_log_msg

REQUIRED_ATTRIBUTES = ['required_attributes']
logger = logging.getLogger('project_logger').getChild(__name__)

DjangoFilterBackend
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
    filter_backends = api_settings.DEFAULT_FILTER_BACKENDS

    def get(self, request: Request, *args, **kwargs) -> Response:
        self.initialize(REQUIRED_ATTRIBUTES)
        # dynamic attributes
        queryset = self.get_queryset()
        caller = self.caller

        method = request.method

        if kwargs.get('pk', None):
            serialized_data = self._get_retrieve_data(**kwargs)
            logger.info(create_log_msg(method, caller, values=kwargs))
        else:
            serialized_data = self._get_list_data(self.filter_queryset(queryset))
            logger.info(create_log_msg(method, caller))

        response = Response(serialized_data, status=self.status)
        return response

    def get_queryset(self):
        # filter_backend = self._get_filter_backend()
        # if filter_backend:
        #     return filter_backend.filter_query(self.request, self.queryset)
        return self.queryset

    def filter_queryset(self, queryset):
        # from generic api view
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

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

    def _get_filter_backend(self):
        attributes = type(self).__dict__
        if 'search_fields' in attributes or 'ordering_fields' in attributes:
            return api_settings.DEFAULT_FILTER_BACKENDS
        else:
            raise AttributeError(
                "if you want to use filter backend, need either 'search_fields' or 'ordering_fields' attribute")


class LimitPagination(LimitOffsetPagination):
    def get_paginated_response(self, data: List) -> OrderedDict:
        return OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ])

# -----------------------------잠시 보류-------------------------------
# default
class FilterBackend:
    """
    ------------------------------------------
    GetMixin
    <class attributes>
        filter_class: FilterBackend
        search_fields: 검색에 사용될 필드
        (optional)ordering_fields: 정렬에 사용될 필드
    ------------------------------------------
    <class>
    FilterSet: view의 속성에 저장된 필터 클래스
    <public method>
        def order(**kwarg) -> QuerySet: queryset 정렬
        def search(**kwarg) -> QuerySet: queryset 검색
        def get_filter_fields() -> dict: view에 정의된 'search_fields', 'ordering_fields' 항목을 반환
        def filter_query() -> QuerySet: get_queryset()을 이용해 필터링된 쿼리셋 반환
            - get_filter_fields()이후 order() 또는 search() 호출을 통해 쿼리문을 정렬 또는 필터링
    ------------------------------------------
    """

    def order(self, **kwargs):
        order = kwargs['order']  # reverse, order

    def search(self, **kwargs):
        pass

    def get_filter_fields(self):
        if hasattr(self, 'order_fields'):
            self.order()

    def filter_query(self, request, queryset) -> QuerySet:
        kwargs = self.get_filter_kwargs(request, queryset)
        query_params = kwargs['data']
        queryset = kwargs['queryset']  # {'username': 'jh'}

        # for key, value in query_params:
        #     queryset.filter(key=value)
        queries = [
            models.Q(**{lookup: term})
            for lookup, term in query_params
        ]

        return queryset

    def get_filter_kwargs(self, request, queryset):
        return {
            'data': request.query_params,
            'queryset': queryset,
            'request': request,
        }

# class Order:
#     pass
#
# class Search:
#     pass
#
# class FilterHandler:
#     pass
