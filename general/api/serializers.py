from rest_framework import serializers
from general.models import User, Post, Chat, Message
from django.db.models import Q


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
            'role',
        )

    def validate(self, data):
        data['role'] = 'user'
        return data

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data['role'],
        )
        user.set_password(validated_data['password'])
        user.save()

        return user


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name")


class PostListSerializer(serializers.ModelSerializer):
    author = UserShortSerializer()
    body = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "title",
            "body",
            "created_at",
        )
    def get_body(self, obj) -> str:
        if len(obj.body) > 128:
            return obj.body[:125] + "..."
        return obj.body
    

class PostRetrieveSerializer(serializers.ModelSerializer):
    author = UserShortSerializer()

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "title",
            "body",
            "created_at",
        )

# для создания и обновления поста
class PostCreateUpdateSerialzier(serializers.ModelSerializer):
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )
    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "title",
            "body",
        )


class ChatSerializer(serializers.ModelSerializer):
    user_1 = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Chat 
        fields = ("user_1", "user_2")

    def create(self, validated_data):
        request_user = validated_data["user_1"]
        second_user = validated_data["user_2"]

        chat = Chat.objects.filter(
            Q(user_1=request_user, user_2=second_user)
            | Q(user_1=second_user, user_2=request_user)
        ).first()
        if not chat:
            chat = Chat.objects.create(
                user_1=request_user,
                user_2=second_user,
            )
        return chat
    

class MessageListSerializer(serializers.ModelSerializer):
    message_author = serializers.CharField()

    class Meta:
        model = Message 
        fields = ("id", "content", "message_author", "created_at")


class ChatListSerializer(serializers.ModelSerializer):
    companion_name = serializers.SerializerMethodField()
    last_message_content = serializers.SerializerMethodField()
    last_message_datetime = serializers.DateTimeField()

    class Meta:
        model = Chat
        fields = (
            "id",
            "companion_name",
            "last_message_content",
            "last_message_datetime",
        )

    def get_last_message_content(self, obj) -> str:
        return obj.last_message_content
    
    def get_companion_name(self, obj) -> str:
        companion = obj.user_1 if obj.user_2 == self.context["request"].user else obj.user_2
        return f"{companion.first_name} {companion.last_name}"
    

class MessageSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )

    def validate(self, attrs):
        chat = attrs["chat"]
        author = attrs["author"]
        if chat.user_1 != author and chat.user_2 != author:
            raise serializers.ValidationError("Вы не являетесь участником этого чата")
        return super().validate(attrs)
    
    class Meta:
        model = Message
        fields = ("id", "author", "content", "chat", "created_at")