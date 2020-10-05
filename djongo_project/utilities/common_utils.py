import logging
from collections import OrderedDict
from functools import wraps
from typing import List

from redis.exceptions import ConnectionError
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.request import Request
from rest_framework.response import Response

from config.log_msg import create_log_msg
from exceptions.api_exception import InvalidFields
from exceptions.common_exceptions import RetryLimitError, ClassMisconfiguration

RETRIES_LIMIT = 3
REQUIRED_ATTRIBUTES = ['required_attributes']

logger = logging.getLogger('project_logger').getChild(__name__)


def with_retry(retries_limit: int = RETRIES_LIMIT, allowed_exceptions=None):
    allowed_exceptions = allowed_exceptions or (ConnectionError,)

    def retry(operation):
        @wraps(operation)
        def wrapped(*args, **kwargs):
            logger = logging.getLogger('project_logger').getChild(__name__)
            last_raised = None
            for _ in range(retries_limit):
                try:
                    return operation(*args, **kwargs)
                except allowed_exceptions as e:
                    error_msg = e.args[0]
                    last_raised = RetryLimitError(detail=error_msg)
            logger.warning('not connect redis server')
            raise last_raised

        return wrapped

    return retry


class SerializerHandler:
    def __init__(self, data, serializer_obj, caller):
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
        raise exc_type(exc_val)


class BaseMixin:
    def initialize(self, attribute_list: List[str]) -> None:
        try:
            for attribute_name in attribute_list:
                self._set_attributes(self.__class__.__dict__[attribute_name])
        except KeyError as ke:
            key_name = str(ke)
            caller_name = self.__class__.__name__
            raise ClassMisconfiguration(detail=f"{caller_name} do not have {key_name} attribute")

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = {
            'request': self.request,
            'view': self
        }
        return self.serializer(*args, **kwargs)

    def _set_attributes(self, attribute_dict) -> None:
        for name, attribute in attribute_dict.items():
            if attribute is not None:
                setattr(self, name, attribute)
            else:
                raise ClassMisconfiguration(detail=f"'{name}' attribute at {self.__class__.__name__} cannot be None!")
        setattr(self, 'caller', self.__class__.__name__)


class PostMixin(BaseMixin):
    """
        필수 속성(required_attributes)
        - serializer
        - status
        동적으로 추가된 속성
        - caller
    """

    def post(self, request: Request) -> Response:
        self.initialize(REQUIRED_ATTRIBUTES)
        data = request.data
        serializer_obj = self.get_serializer(data=data)
        serializer_name = serializer_obj.__class__.__name__

        # dynamic attributes
        caller = self.caller
        status = self.status

        with SerializerHandler(data, serializer_obj, caller) as validated_data:
            if 'Regist' in serializer_name and getattr(serializer_obj, 'create', None):
                serializer_obj.create(validated_data)
                logger.info(create_log_msg(self, caller, validated_data))

        response = Response(validated_data, status=status)
        logger.info(create_log_msg(self, caller))
        return response


class GetMixin(BaseMixin):
    """
        필수 속성(required_attributes)
        - serializer
        - status
        - queryset
    """

    def get(self, request: Request, *args, **kwargs) -> Response:
        self.initialize(REQUIRED_ATTRIBUTES)
        queryset = self.queryset
        caller = self.caller

        if kwargs.get('pk', None):
            serialized_data = self._get_retrieve_data(**kwargs)
            logger.info(create_log_msg(self, caller, kwargs))
        else:
            serialized_data = self._get_list_data(queryset)
            logger.info(create_log_msg(self, caller))

        response = Response(serialized_data, status=self.status)
        return response

    def _get_list_data(self, queryset) -> OrderedDict:
        paginator = LimitPagination()
        page = paginator.paginate_queryset(queryset, self.request)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = paginator.get_paginated_response(serializer.data)
            return data

        serializer = self.get_serializer(queryset, many=True)
        return serializer.data

    def _get_retrieve_data(self, **kwargs):
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
