from django.db import models
from django.contrib.auth.models import AbstractUser


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
