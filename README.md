# DRF HTTP Serialization

**A collection of useful Decorators to DRY up your Django Rest Framework when using Serializers**

Full documentation: <https://drf-http-serialization.readthedocs.io/en/latest/>

## Overview

Serializer decorators help you boost your code and decrease duplication
by using a higher-order function to reduce the number of lines of code
and maintain consistency in your project.

## Requirements

- Python (>= 3.7)
- [Django](https://github.com/django/django) (>= 3.0)
- [Django REST Framework](https://github.com/tomchristie/django-rest-framework) (> 3.11)

## Installation

Using `pip`:

```bash
$ pip install drf-http-serialization
```

## Basic Usage

**HttpSerialization**

```py
# model user
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass
```

```py
# serializers.py
from rest_framework import serializers
from drf_http_serialization.models import User

class UserInformationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    username = serializers.CharField()

    class Meta:
        model = User
        fields = ["id", "email", "username"]
```

- With `@api_view` decorator function

```py
from rest_framework.decorators import api_view
from drf_http_serialization import HttpSerialization
from drf_http_serialization.serializers import UserInformationSerializer

@api_view(http_method_names=["GET"])
@HttpSerialization(serializer_cls=UserInformationSerializer)
def get_user_func_view(request):
    return request.user
```

API response

```json
{
  "data": {
    "id": 1,
    "email": "userA@example.com",
    "username": "userA"
  }
}
```

- With `GenericViewSet` class

```py
from drf_http_serialization import HttpSerialization
from rest_framework.viewsets import GenericViewSet
from drf_http_serialization.models import User
from drf_http_serialization.serializers import UserInformationSerializer
# ...


class UserViewSet(GenericViewSet):
    def get_queryset(self):
        return User.objects.all()

    @HttpSerialization(serializer_cls=UserInformationSerializer)
    def list(self, request):
        return self.get_queryset()
```

API response

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "data": [
    {
      "id": 1,
      "email": "tom_hiddleston@gmail.com",
      "username": "tom_hiddleston"
    },
    {
      "id": 2,
      "email": "chris_hemsworth@gmail.com",
      "username": "chris_hemsworth"
    }
  ]
}
```

- With `APIView` class

```py
from rest_framework.views import APIView
from drf_http_serialization import HttpSerialization
from drf_http_serialization.serializers import UserInformationSerializer


class UserAPIView(APIView):
    @HttpSerialization(serializer_cls=UserInformationSerializer)
    def get(self, request):
        return request.user
```

**SchemaValidation**

- When validating body data(`POST` method)

```py
from rest_framework.views import APIView
from drf_http_serialization import HttpSerialization, SchemaValidation
from drf_http_serialization.serializers import UserInformationSerializer
from drf_http_serialization.models import User

# combination usage
class UserAPIView(APIView):
    @HttpSerialization(serializer_cls=UserInformationSerializer)
    @SchemaValidation(serializer_cls=UserInformationSerializer, location="body")
    def create(self, request, data):
        # data object is validated
        # the default will use key `data`, if you want to use another key,
        # add argument to_key="something" in SchemaValidation
        user = User.objects.create(**data)
        return user
```

API call

```bash
POST /api/users HTTP/1.1
Host: 127.0.0.1
Content-Type: application/json
Accept: */*


{
  "email": "chris.evans",
  "username": "chris_evans"
}

```

API response (422 HTTP status's code)

```json
{
  "errors": [
    {
      "field": "email",
      "detail": ["Enter a valid email address."]
    }
  ],
  "message": "Validation Error!"
}
```

- When validating query params

```py
from drf_http_serialization import HttpSerialization, SchemaValidation
from drf_http_serialization.serializers import UserInformationSerializer
from drf_http_serialization.models import User
from rest_framework.viewsets import GenericViewSet

class UserViewSet(GenericViewSet):

    # combination usage
    @HttpSerialization(serializer_cls=UserInformationSerializer)
    @SchemaValidation(serializer_cls=UserInformationSerializer, location="query")
    def list(self, request, query):
        # data dict is validated
        # the default will use key `data`, if you want to use another key,
        # add argument to_key="something" in SchemaValidation
        user = User.objects.filter(username=query["username"])
        return user
```

API call

```
GET /api/users?email=chris_evans HTTP/1.1
```

API response(422 HTTP status's code)

```json
{
  "errors": [
    {
      "field": "email",
      "detail": ["Enter a valid email address."]
    }
  ],
  "message": "Validation Error!"
}
```

Accept list query params lookup:

```py
from drf_http_serialization import HttpSerialization, SchemaValidation
from drf_http_serialization.serializers import UserListLookUpSerializer, UserInformationSerializer
from drf_http_serialization.models import User
from rest_framework.viewsets import GenericViewSet

class UserViewSet(GenericViewSet):

    # combination usage
    @HttpSerialization(serializer_cls=UserInformationSerializer)
    @SchemaValidation(serializer_cls=UserListLookUpSerializer, location="query")
    def list(self, request, query):
        # query dict is validated
        # the default will use key `query`, if you want to use another key,
        # add argument to_key="something" in SchemaValidation
        user = User.objects.filter(username__in=query["username"])
        return user
```

API request

```
GET /api/users?username=chris_evans&username=tom_hiddleston HTTP/1.1
```

API response

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "data": [
    {
      "id": 1,
      "email": "tom_hiddleston@gmail.com",
      "username": "tom_hiddleston"
    },
    {
      "id": 3,
      "email": "chris.evans@gmail.com",
      "username": "chris_evans"
    }
  ]
}
```

## Support

If you need help, don't hesitate to start an [issue][issue].
For commercial support, please contact via email:
[Thang Dang Minh](mailto:thangdangdev@gmail.com?subject=[GitHub]%20Source%20Django%20HTTP%20Serialization)

[issue]: https://github.com/tkppro/drf-http-serialization/issues
