from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    fullname = models.CharField(max_length=100, null=False, blank=False)

    # Falta agregar algunaas cosas. Avatar...
    # Registrar las ultimas partidas, un modelo aparte con vinculo al user?


    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name='customuser_set',  # Choose a suitable related_name
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='customuser_set',  # Choose a suitable related_name
        related_query_name='user',
    )