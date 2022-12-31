from rest_framework.viewsets import GenericViewSet


class TestView(GenericViewSet):
    def list(self, request):
        print("abc")
