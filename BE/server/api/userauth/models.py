from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, null=False, blank=False)
    fullname = models.CharField(max_length=100, null=False, blank=False)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def update_avatar(self, new_avatar):
        if self.avatar:
            self.avatar.delete()

        self.avatar = new_avatar
        self.save()


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