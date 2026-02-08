from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True)

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # change from default 'user_set'
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',  # change from default 'user_set'
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )


    def __str__(self):
        return self.username



        