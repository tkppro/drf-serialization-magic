**HttpSerialization**

* With `@api_view` decorator function
```py
from rest_framework.decorators import api_view
from drf_http_serialization import HttpSerialization
from drf_http_serialization.serializers import UserInformationSerializer

@api_view(http_method_names=["GET"])
@HttpSerialization(serializer_cls=UserInformationSerializer)
def get_user_func_view(request):
    return request.user
```


* With `GenericViewSet` class
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
    def list(self, request, pk):
        return self.get_queryset()

```

* With `APIView` class
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

* When validating body data(`POST` method)
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


* When validating query params
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
