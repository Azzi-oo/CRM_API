from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin
from general.api.serializers import UserRegistrationSerializer


class UserViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = UserRegistrationSerializer
