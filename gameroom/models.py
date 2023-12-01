from django.db import models
from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify

User = get_user_model()

class Game(models.Model):
    game_name = models.CharField(max_length=32)
    slug = models.SlugField(default="Mr-slug-will-change-on-creation")
    number_of_players = models.IntegerField(default=2)
    word_bank_size = models.IntegerField(default=5)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    # def getCurrentPlayers(self):
    #     return PamplesneakInfo.objects.filter(current_game=self).count()

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.game_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.game_name

class Player(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="game_game")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="game_user")
    name = models.CharField(max_length=64, null=True, blank=True)
    nick = models.CharField(max_length=64, null=True, blank=True)
    succesful_sneaks = models.IntegerField(default=0)
    failed_sneaks = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Word(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey('Player', on_delete=models.SET_NULL, related_name='player_player', null=True, blank=True)
    word = models.CharField(max_length=64)
    created_by = models.ForeignKey('Player', on_delete=models.SET_NULL, related_name='player_created_by', null=True, blank=True)
    send_to = models.ForeignKey('Player', on_delete=models.SET_NULL, related_name='player_sent_to', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.word
