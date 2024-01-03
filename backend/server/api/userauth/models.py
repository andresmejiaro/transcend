from django.db import models
# Create your models here.
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import JSONField
from django.utils import timezone


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, null=False, blank=False)
    fullname = models.CharField(max_length=100, null=False, blank=False)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    login = models.CharField(max_length=100, null=True, blank=True, default=None)

    def update_avatar(self, new_avatar):
        if self.avatar:
            self.avatar.delete()

        self.avatar = new_avatar
        self.save()

    is_2fa_enabled = models.BooleanField(default=False)
    is_2fa_setup_complete = models.BooleanField(default=False)
    secret_key = models.CharField(max_length=255, null=True, blank=True)
    def enable_2fa(self, secret_key):
        self.is_2fa_enabled = True
        self.secret_key = secret_key
        self.save()

    def disable_2fa(self):
        self.is_2fa_enabled = False
        self.secret_key = None
        self.is_2fa_setup_complete = False
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

    ELO = models.IntegerField(default=0)

    list_of_sent_invites = JSONField(default=list, blank=True)
    list_of_received_invites = JSONField(default=list, blank=True)


    def add_received_invites(self, invite_id, invite_type):
        self.list_of_received_invites.append({
            'invite_id': invite_id,
            'invite_type': invite_type,
            'time': timezone.now().isoformat(),
        })
        self.save()

    def remove_received_invites(self, invite_id, invite_type):
        self.list_of_received_invites = [
            invite for invite in self.list_of_received_invites
            if not (invite['invite_id'] == invite_id and invite['invite_type'] == invite_type)
        ]
        self.save()

    def add_sent_invites(self, invite_id, invite_type):
        self.list_of_sent_invites.append({
            'invite_id': invite_id,
            'invite_type': invite_type,
            'time': timezone.now().isoformat(),
        })
        self.save()

    def remove_sent_invites(self, invite_id, invite_type):
        self.list_of_sent_invites = [
            invite for invite in self.list_of_sent_invites
            if not (invite['invite_id'] == invite_id and invite['invite_type'] == invite_type)
        ]
        self.save()

    def get_sent_invites(self):
        return self.list_of_sent_invites
    
    def get_received_invites(self):
        return self.list_of_received_invites

    def __str__(self):
        return f'{self.id} {self.username}'
    


class Friendship(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='user_friends')
    friends = models.ManyToManyField(CustomUser, related_name='friends', blank=True)
    blocked_users = models.ManyToManyField(CustomUser, related_name='blocked_users', blank=True)

    def __str__(self):
        return f'{self.user.id} {self.user.username}\'s friends'