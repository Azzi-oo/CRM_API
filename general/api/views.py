from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin, DestroyModelMixin
from general.api.serializers import UserRegistrationSerializer, PostListSerializer, PostRetrieveSerializer, PostCreateUpdateSerialzier, ChatSerializer, MessageListSerializer, ChatListSerializer, MessageSerializer
from general.models import Post, Chat, Message
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db.models import F, Case, When, CharField, Value
from django.http import HttpResponse
from rest_framework.decorators import action
from django.db.models import Q, OuterRef, Subquery


class UserViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = UserRegistrationSerializer


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all().order_by("-id")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        elif self.action == "retrieve":
            return PostRetrieveSerializer
        return PostCreateUpdateSerialzier
    
    def perform_update(self, serializer):
        instance = self.get_object()

        if instance.author != self.request.user:
            raise PermissionDenied("Вы не являетесь автором этого поста")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("Вы не являетесь автором этого поста")
        instance.delete()


class ChatViewSet(
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == "list":
            return ChatListSerializer
        if self.action == "messages":
            return MessageListSerializer
        return ChatSerializer
    
    def get_queryset(self):
        user = self.request.user

        last_message_subquery = Message.objects.filter(
            chat=OuterRef('pk')
        ).order_by('-created_at').values('created_at')[:1]
        last_message_content_subquery = Message.objects.filter(
            chat=OuterRef('pk')
        ).order_by('-created_at').values('content')[:1]

        qs = Chat.objects.filter(
            Q(iser_1=user) | Q(user_2=user),
            messagees__isnull=False,
        ).annotate(
            last_message_datetime=Subquery(last_message_subquery),
            last_message_content=Subquery(last_message_content_subquery),
        ).select_related(
            "user_1",
            "user_2",
        ).order_by("-last_message_datetime").distinct()
        return qs
    
    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        messages = self.get_object().messages.filter(chat__id=pk).annotate(
            message_author=Case(
                When(author=self.request.user, then=Value("Вы")),
                default=F("author__first_name"),
                output_field=CharField(),
            )
        ).order_by("-created_at")
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    

class MessageViewSet(
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = MessageSerializer 
    permission_classes = [IsAuthenticated]
    queryset = Message.objects.all().order_by("-id")

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("Вы не являетесь автором этого сообщения")
        instance.delete()