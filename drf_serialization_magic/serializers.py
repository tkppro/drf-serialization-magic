from rest_framework import serializers
from drf_serialization_magic.models import User


class UserInformationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    username = serializers.CharField()

    class Meta:
        model = User
        fields = ["id", "email", "username"]


class UserListLookUpSerializer(serializers.ModelSerializer):
    username = serializers.ListField(child=serializers.CharField)

    class Meta:
        model = User
        fields = ["id", "email", "username"]
