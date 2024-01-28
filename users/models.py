from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=32, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="user_profile"
    )
    current_game = models.ForeignKey(
        "gameroom.Game",
        related_name="player_current_game",
        on_delete=models.SET_NULL,  # Update the on_delete action
        blank=True,
        null=True,
    )
    previous_games = models.ManyToManyField(
        "gameroom.Game", related_name="player_previous_games", blank=True
    )

    current_player = models.ForeignKey(
        "gameroom.Player",
        related_name="current_player",
        on_delete=models.SET_NULL,  # Update the on_delete action
        blank=True,
        null=True,
    )
    previous_players = models.ManyToManyField(
        "gameroom.Player", related_name="previous_players", blank=True
    )

    games_played = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    loses = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class PushSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subscription_json = models.TextField()  # Store the subscription data as JSON

    def __str__(self):
        return f"Subscription for {self.user.username}"
