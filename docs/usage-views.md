**RenderSerialization**

* With `@api_view` decorator function

```py
from rest_framework.decorators import api_view
from drf_serialization_magic import RenderSerialization
from drf_serialization_magic.serializers import UserInformationSerializer


@api_view(http_method_names=["GET"])
@RenderSerialization(serializer_cls=UserInformationSerializer)
def get_user_func_view(request):
    return request.user
```


* With `GenericViewSet` class

```py
from drf_serialization_magic import RenderSerialization
from rest_framework.viewsets import GenericViewSet
from drf_serialization_magic.models import User
from drf_serialization_magic.serializers import UserInformationSerializer
# ...


class UserViewSet(GenericViewSet):
    def get_queryset(self):
        return User.objects.all()

    @RenderSerialization(serializer_cls=UserInformationSerializer)
    def list(self, request):
        return self.get_queryset()

```

* With `APIView` class

```py
from rest_framework.views import APIView
from drf_serialization_magic import RenderSerialization
from drf_serialization_magic.serializers import UserInformationSerializer


class UserAPIView(APIView):
    @RenderSerialization(serializer_cls=UserInformationSerializer)
    def get(self, request):
        return request.user
```

**ValidateSerialization**

* When validating body data(`POST` method)

```py
from rest_framework.views import APIView
from drf_serialization_magic import RenderSerialization, ValidateSerialization
from drf_serialization_magic.serializers import UserInformationSerializer
from drf_serialization_magic.models import User


# combination usage
class UserAPIView(APIView):
    @RenderSerialization(serializer_cls=UserInformationSerializer)
    @ValidateSerialization(serializer_cls=UserInformationSerializer, location="body")
    def create(self, request, data):
        # data object is validated
        # the default will use key `data`, if you want to use another key,
        # pass argument to_key="something" in ValidateSerialization
        user = User.objects.create(**data)
        return user
```


* When validating query params

```py
from drf_serialization_magic import RenderSerialization, ValidateSerialization
from drf_serialization_magic.serializers import UserInformationSerializer
from drf_serialization_magic.models import User
from rest_framework.viewsets import GenericViewSet


class UserViewSet(GenericViewSet):

    # combination usage
    @RenderSerialization(serializer_cls=UserInformationSerializer)
    @ValidateSerialization(serializer_cls=UserInformationSerializer, location="query")
    def list(self, request, query):
        # data dict is validated
        # the default will use key `data`, if you want to use another key,
        # pass argument to_key="something" in ValidateSerialization
        user = User.objects.filter(username=query["username"])
        return user
```
