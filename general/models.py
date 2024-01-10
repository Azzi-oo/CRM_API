from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import UniqueConstraint, F, functions

class User(AbstractUser):
    friends = models.ManyToManyField(
        to='self',
        symmetrical=True,
        blank=True,
    )

    groups = models.ManyToManyField(
        to='auth.Group',
        related_name='custom_user_set',
        blank=True,
    )

    user_permissions = models.ManyToManyField(
        to='auth.Permission',
        related_name='custom_user_set',
        blank=True,
    )

    role = models.CharField(max_length=100, blank=True, null=True)


class Post(models.Model):
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    title = models.CharField(max_length=64)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    body = models.TextField()
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    post = models.ForeignKey(
        to=Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Chat(models.Model):
    user_1 = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="chats_as_user1",
    )
    user_2 = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="chats_as_user2",
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                functions.Greatest(F('user_1'), F('user_2')),
                functions.Least(F('user_1'), F('user_2')),
                name="users_chat_unique",
            ),
        ]


class Message(models.Model):
    content = models.TextField()
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    chat = models.ForeignKey(
        to=Chat,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    created_at = models.DateTimeField(auto_now_add=True)
