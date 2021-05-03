from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


FOLLOW_CHOICES = (
    ('Follow', 'Follow'),
    ('Followed', 'Followed'),
    ('UnFollow', 'UnFollow'),)


class UserFollowing(models.Model):
    followed_user = models.ForeignKey(User, related_name="followed", related_query_name='followed', on_delete=models.CASCADE, null=True, default=None)
    following_user = models.ForeignKey(User, related_name="follower",  related_query_name='follower', on_delete=models.CASCADE, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True)
    value = models.CharField(choices=FOLLOW_CHOICES, default="Follow", max_length=10)

