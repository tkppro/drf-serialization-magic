import functools

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _
from rest_framework.fields import CharField, DateField, BooleanField, DateTimeField
from typing import Any, Union

from django.db.models import QuerySet
from django.http import QueryDict, HttpRequest
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.serializers import SerializerMetaclass
from rest_framework.settings import api_settings


class BaseSerializationHandler:
    default_error_message = _("Validation Error!")
    unknown_error_message = _("An unknown error occurred.")
    unknown_field = "unknown"

    def __init__(
        self,
        serializer_cls: SerializerMetaclass = None,
        paginator=api_settings.DEFAULT_PAGINATION_CLASS(),
        error_messages=None,
    ):
        self._serializer_cls = serializer_cls

        self.error_messages = (
            error_messages
            if error_messages
            else getattr(self, "default_error_message", "")
        )
        self._paginator = paginator

    def _extract_request(self, *args, **kwargs):
        if len(args) == 1:
            return args[0]
        elif len(args) == 2:
            # in case of class method , `self` is first arg
            return args[1]
        else:
            raise AttributeError(
                "Cannot extract request from type: {}".format(type(args))
            )

    def wrap_errors(self, data=None):
        # TODO refactor to be extended in any kind of format
        # Helper function to extract errors from a dictionary
        def _extract_detail_error(errs):
            # Use a list comprehension to create a list of error dictionaries
            return [{"field": k, "detail": v} for k, v in errs.items()]

        # Check if the data is a dictionary
        if isinstance(data, dict):
            # If it is, return the errors extracted from the dictionary
            return {
                "errors": _extract_detail_error(data),
                "message": self.default_error_message,
            }

        # Check if the data is a list (data is always dict, so this check is useless)
        elif isinstance(data, list):
            # If it is, return the errors extracted from each element in the list
            return {
                "errors": [_extract_detail_error(i) for i in data],
                "message": self.default_error_message,
            }
        # If the data is neither a dictionary nor a list, return an error with an unknown field
        else:
            return {
                "errors": [{"field": self.unknown_field, "detail": data}],
                "message": self.unknown_error_message,
            }

    def unwrap_pagination(
        self,
        resp,
        request,
    ) -> Response:
        """
        Function to serialize data for type(list, Model, QuerySet...)
        and perform pagination on the Iterable object

        Parameters:
            resp (Any[Response, QuerySet, List, dict, Model]): response data from the decorated function.
                Can be a `Response` object, a `QuerySet`, a list, a dictionary, or a model instance.
            serializer (SerializerMetaclass): serializer class to be used for serializing the data
            request (HttpRequest): request object containing the request details
            paginator: Pagination class to be used for paginating the data. Defaults to the
                    pagination class specified in the Django REST framework settings.
        Returns:
            response: return serialized data in Response body
        """

        # If the response is already a Response object, return it as-is
        if isinstance(resp, Response):
            return resp
        # If the response is a QuerySet or list, paginate the data
        if isinstance(resp, (QuerySet, list)):
            # Get the paginated data
            page = self._paginator.paginate_queryset(resp, request)
            # If there is paginated data, serialize and return it
            if page is not None:
                try:
                    # If the data is a list of dictionaries and there is no serializer, return the data as-is
                    if isinstance(resp[0], dict) and not self._serializer_cls:
                        data = page
                    # Otherwise, serialize the data using the provided serializer
                    else:
                        data = self._serializer_cls(
                            page, many=True, context={"request": request}
                        ).data
                # If there are no elements in the list, return an empty list
                except IndexError:
                    data = []
                # Return the paginated data as a response
                return self._paginator.get_paginated_response(data)
            # If there is no paginated data, return an empty list
            return Response([])
        # If the response is not a QuerySet or list, serialize the data and return it
        else:
            # If the data is a dictionary and there is no serializer, return the data as-is
            if isinstance(resp, dict) and not self._serializer_cls:
                return Response(resp)
            # Otherwise, serialize the data using the provided serializer
            else:
                serializer = self._serializer_cls(resp, context={"request": request})
                return Response({"data": serializer.data})


class RenderSerialization(BaseSerializationHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self, func):
        """
        Decorator function to serialize data before response
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get the request object
            request = self._extract_request(*args, **kwargs)
            # Get the query parameters
            try:
                # Call the decorated function
                resp = func(*args, **kwargs)
            except ValidationError as e:
                # Return a response with validation errors, if any
                return Response(self.wrap_errors(e.detail), status=422)

            # Serialize the data and return the response
            return self.unwrap_pagination(resp, request)

        return wrapper


class ValidateSerialization(BaseSerializationHandler):
    SINGLE_FIELD_TYPE = (CharField, DateField, BooleanField, DateTimeField)
    default_dict_key = {"header": "query", "body": "data"}

    def __init__(self, location=None, to_key=None, **kwargs):
        super().__init__(**kwargs)
        self.location = location
        self._to_key = to_key if to_key else self.default_dict_key[location]
        if location == "body":
            self._body_validation = True
        elif location == "header":
            self._body_validation = False
        else:
            raise ImproperlyConfigured(
                "System cannot accept with location: {}".format(location)
            )

    def _parse_type(self, v: Any) -> Union[int, float, str]:
        if type(v) is int:
            return v
        elif type(v) is float:
            return v
        elif type(v) is str:
            try:
                return int(v)
            except ValueError:
                try:
                    return float(v)
                except ValueError:
                    return str(v)
        else:
            raise TypeError(f"Unable to parse type for value: {v}")

    def convert_type_query_params(self, params: QueryDict) -> dict:
        """
        Function to convert query params type to numeric, boolean, string...
        """

        def _inner_processing(field_key: str, field_value: Any):
            if self._serializer_cls:
                # Get serializer field
                _serializer = self._serializer_cls()
                field = _serializer.get_fields().get(field_key)

                # Check if the field is a CharField, DateField, or BooleanField
                if type(field) in self.SINGLE_FIELD_TYPE:
                    # Only one item in list, if more than one, it will raise ValidationError
                    if len(field_value) == 1:
                        # Parse to string
                        return self._parse_type(field_value[0])

                # No serializer or field is not a CharField, DateField, or BooleanField
                # Convert all values in the list to numeric or string types
            return [self._parse_type(el) for el in field_value]

        converted_params = dict()
        # loop over each params, by default, the type of each is list
        for k, v in params.lists():
            converted_params[k] = _inner_processing(k, v)

        return converted_params

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request = self._extract_request(*args, **kwargs)
            try:
                if self._serializer_cls is not None:
                    if self._body_validation:
                        data = request.data
                    else:
                        data = request.query_params
                        data = self.convert_type_query_params(data)
                    # get body data
                    _serializer = self._serializer_cls(data=data)
                    _serializer.is_valid(raise_exception=True)
                    # assign query with a key
                    kwargs[self._to_key] = _serializer.data

                return func(*args, **kwargs)

            except ValidationError as e:
                return Response(self.wrap_errors(e.detail), status=422)

        return wrapper
