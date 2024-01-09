from django.contrib import admin
from .models import Game, Round, Player, Word, Vote, ExampleWord


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ["game_name", "number_of_players", "active", "created"]
    # Add more admin options as needed


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ["game", "round_number", "state"]
    # Add more admin options as needed


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ["name", "game", "succesful_sneaks", "failed_sneaks"]
    # Add more admin options as needed


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ["word", "game", "created"]
    # Add more admin options as needed


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ["word", "player", "vote_type"]
    # Add more admin options as needed


@admin.register(ExampleWord)
class ExampleWordAdmin(admin.ModelAdmin):
    list_display = ["word", "category", "difficulty"]
    list_filter = ["category", "difficulty"]
    # Add more admin options as needed
