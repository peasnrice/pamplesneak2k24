# tasks.py
from celery import shared_task
from .models import Game, Round, Player, Word, ExampleWord
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
import json
import random
from collections import defaultdict


@shared_task
def send_game_start_message(game_id):
    channel_layer = get_channel_layer()
    group_name = f"gameroom_{game_id}"
    message = {"type": "game.start"}
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "game_start",
            "text": json.dumps(message),
        },
    )


@shared_task
def round_transition_state(game_id):
    # Set the round to the transition state
    game = Game.objects.get(id=game_id)
    current_round = game.current_round
    round = Round.objects.get(game=game, round_number=current_round)
    round.state = "transition"
    round.state_start_time = timezone.now()
    round.save()
    countdown_time = round.transition_state_duration.total_seconds()

    # Notify clients of the transition stateåç
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"gameroom_{game_id}",
        {
            "type": "round.transition",
            "round_state": round.state,
            "round_number": current_round,
            "countdown_time": countdown_time,
        },
    )

    # Schedule the start_round task to run after the transition period
    start_create_state.apply_async((game_id,), countdown=countdown_time)


@shared_task
def start_create_state(game_id):
    game = Game.objects.get(id=game_id)
    current_round = game.current_round
    round = Round.objects.get(game=game, round_number=current_round)
    countdown_time = round.create_state_duration.total_seconds()
    # Change round state from 'transition' to 'create'
    round.state = "create"
    round.state_start_time = timezone.now()
    round.save()

    # Notify all clients to show the round screen
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"gameroom_{game_id}",
        {
            "type": "round.create",
            "round_state": round.state,
            "round_number": current_round,
            "countdown_time": countdown_time,
        },
    )
    start_play_state.apply_async((game_id,), countdown=countdown_time)


@shared_task
def start_play_state(game_id):
    game = Game.objects.get(id=game_id)
    current_round = game.current_round
    round = Round.objects.get(game=game, round_number=current_round)
    countdown_time = round.play_state_duration.total_seconds()
    round.state = "play"
    round.state_start_time = timezone.now()
    round.save()

    players = list(Player.objects.filter(game=game))
    number_of_players = len(players)
    sneaks_per_round = round.sneaks_per_round
    total_sneaks_required = number_of_players * sneaks_per_round

    # Calculate total words submitted
    total_words_submitted = Word.objects.filter(round=round, game=game).count()

    # Determine shortfall and create words from ExampleWord if needed
    shortfall = total_sneaks_required - total_words_submitted
    if shortfall > 0:
        for _ in range(shortfall):
            example_word = random.choice(list(ExampleWord.objects.all()))
            Word.objects.create(
                word=example_word.word,
                round=round,
                game=game,
                # created_by remains None for app-created words
            )

    # Distribute words, ensuring no player receives their own word and everyone gets the same number of sneaks
    # First, collect all words for this round, including newly added words
    all_words = list(
        Word.objects.filter(round=round, game=game).select_related("created_by")
    )

    # Shuffle words to randomize distribution
    random.shuffle(all_words)

    # Initialize distribution data structure
    distribution = {player.id: [] for player in players}

    # Attempt to distribute words evenly, ensuring no self-created words are received
    for word in all_words:
        for player in players:
            if word.created_by is None or word.created_by != player:
                if len(distribution[player.id]) < sneaks_per_round:
                    distribution[player.id].append(word)
                    break

    # Assign words to players based on the distribution
    for player_id, words in distribution.items():
        for word in words:
            word.send_to = Player.objects.get(id=player_id)
            word.save()

    # Notify all clients to show the round screen
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"gameroom_{game_id}",
        {
            "type": "round.play",
            "round_state": round.state,
            "round_number": current_round,
            "countdown_time": countdown_time,
        },
    )

    end_round.apply_async((game_id,), countdown=countdown_time)


@shared_task
def end_round(game_id):
    game = Game.objects.get(id=game_id)
    current_round = game.current_round
    round = Round.objects.get(game=game, round_number=current_round)
    round.state = "end"
    round.save()

    # Increase current round
    game.current_round += 1
    game.save()
    round.ended = True
    round.save()

    # If more rounds remain, start the next round
    if game.current_round <= game.number_of_rounds:
        round_transition_state.apply_async((game_id,))
    else:
        game.ended = True
        game.current_round = game.number_of_rounds
        game.save()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"gameroom_{game_id}",
            {
                "type": "game.end",
                "round_number": current_round,
            },
        )
