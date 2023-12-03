from django.db import models

class UserFriends(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='user_friends')
    friends = models.ManyToManyField(CustomUser, related_name='friends', blank=True)
    blocked_users = models.ManyToManyField(CustomUser, related_name='blocked_users', blank=True)
    pending_invites = models.ManyToManyField(CustomUser, related_name='pending_invites', blank=True)
    sent_requests = models.ManyToManyField(CustomUser, related_name='sent_requests', blank=True)

    def send_friend_request(self, target_user):
        # Logic to send a friend request
        pass

    def remove_friend(self, friend_user):
        # Logic to remove a friend
        pass


from .models import CustomUser
