from django.db import models
from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify
from django.utils.crypto import get_random_string
from datetime import timedelta
from django.utils import timezone
from django.conf import settings


User = get_user_model()


class Game(models.Model):
    game_name = models.CharField(max_length=32)
    game_room_code = models.CharField(max_length=6, unique=True)
    slug = models.SlugField(default="Mr-slug-will-change-on-creation")
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="hosted_games",
    )
    number_of_players = models.IntegerField(default=1)
    word_bank_size = models.IntegerField(default=5)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    ended = models.BooleanField(default=False)

    number_of_rounds = models.IntegerField(
        default=1, choices=[(i, i) for i in range(1, 13)]
    )

    current_round = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        if not self.id and not self.game_room_code:
            self.game_room_code = self._generate_unique_code()
            self.slug = slugify(self.game_name)
        super().save(*args, **kwargs)

    def _generate_unique_code(self):
        code = get_random_string(length=6).upper()
        # Ensure the code is unique and regenerate if it's not
        while Game.objects.filter(game_room_code=code).exists():
            code = get_random_string(length=6).upper()
        return code

    def __str__(self):
        return self.game_name


class Round(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="rounds")
    round_number = models.IntegerField()
    sneaks_per_round = models.IntegerField(default=3)
    allow_additional_sneaks = models.BooleanField(default=False)
    state_start_time = models.DateTimeField(null=True, blank=True)
    transition_state_duration = models.DurationField(default=timedelta(seconds=10))
    create_state_duration = models.DurationField(default=timedelta(minutes=3))
    play_state_duration = models.DurationField(default=timedelta(minutes=5))
    ended = models.BooleanField(default=False)

    STATE_CHOICES = (
        ("transition", "transition"),
        ("create", "create"),
        ("play", "play"),
        ("end", "end"),
    )
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default="transition")

    def get_remaining_time(self):
        time_elapsed = timezone.now() - self.state_start_time
        if self.state == "transition":
            total_duration = self.transition_state_duration
        elif self.state == "create":
            total_duration = self.create_state_duration
        elif self.state == "play":
            total_duration = self.play_state_duration
        else:
            return None  # Handle other states or errors

        if time_elapsed > total_duration:
            remaining_time = timedelta(seconds=0)
        else:
            remaining_time = total_duration - time_elapsed

        print(remaining_time)
        print(max(remaining_time.total_seconds(), 0))
        return max(remaining_time.total_seconds(), 0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Round {self.round_number} of {self.game.game_name}"


class Player(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="game_game")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="game_user")
    name = models.CharField(max_length=64, null=True, blank=True)
    nick = models.CharField(max_length=64, null=True, blank=True)
    succesful_sneaks = models.IntegerField(default=0)
    failed_sneaks = models.IntegerField(default=0)
    received_sneaks = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Word(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    round = models.ForeignKey(Round, on_delete=models.CASCADE, null=True)
    player = models.ForeignKey(
        "Player",
        on_delete=models.SET_NULL,
        related_name="player_player",
        null=True,
        blank=True,
    )
    word = models.CharField(max_length=128)
    created_by = models.ForeignKey(
        "Player",
        on_delete=models.SET_NULL,
        related_name="player_created_by",
        null=True,
        blank=True,
    )
    send_to = models.ForeignKey(
        "Player",
        on_delete=models.SET_NULL,
        related_name="player_sent_to",
        null=True,
        blank=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    successful = models.BooleanField(null=True)
    skipped = models.BooleanField(null=True)
    validations_count = models.IntegerField(default=0)
    rejections_count = models.IntegerField(default=0)

    def __str__(self):
        return self.word


class Vote(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name="votes")
    player = models.ForeignKey("Player", on_delete=models.CASCADE, related_name="votes")
    vote_type = models.CharField(
        max_length=10, choices=(("validate", "Validate"), ("reject", "Reject"))
    )

    class Meta:
        unique_together = ("word", "player")

    def __str__(self):
        return f"{self.player}'s vote on '{self.word}'"

    def save(self, *args, **kwargs):
        # Call the real save() method
        super().save(*args, **kwargs)

        # Update the Word instance
        validations = Vote.objects.filter(word=self.word, vote_type="validate").count()
        rejections = Vote.objects.filter(word=self.word, vote_type="reject").count()

        # Update the Word instance
        self.word.validations_count = validations
        self.word.rejections_count = rejections
        self.word.save()


class ExampleWord(models.Model):
    word = models.CharField(max_length=128)
    category = models.CharField(max_length=64)
    difficulty = models.IntegerField(default=0)
    note = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        if self.note:
            return f"{self.word} - {self.note}"
        else:
            return self.word
