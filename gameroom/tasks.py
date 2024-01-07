# tasks.py
from celery import shared_task
from .models import Game, Round
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json


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
def start_round(game_id, round_number):
    game = Game.objects.get(id=game_id)
    current_round = game.current_round
    round = Round.objects.get(game=game, round_number=current_round)
    countdown_time = round.duration.total_seconds()
    game.state = "create"
    game.save()

    # Notify all clients to show the round screen
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"gameroom_{game_id}",
        {
            "type": "round.start",
            "round_number": round_number,
            "countdown_time": countdown_time,
        },
    )

    end_round.apply_async(
        (game_id, round_number), countdown=round.duration.total_seconds()
    )


@shared_task
def end_round(game_id, round_number):
    game = Game.objects.get(id=game_id)
    current_round = game.current_round
    round = Round.objects.get(game=game, round_number=current_round)
    countdown_time = round.duration.total_seconds()
    game.state = "play"
    game.save()

    # Notify all clients to show the set screen
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"gameroom_{game_id}",
        {
            "type": "round.end",
            "round_number": round_number,
            "countdown_time": countdown_time,
        },
    )

    # Increase current round
    game.current_round += 1
    game.save()
    round.ended = True
    round.save()

    # If more rounds remain, start the next round
    if game.current_round <= game.number_of_rounds:
        start_round.apply_async(
            (game_id, game.current_round),
            countdown=round.time_between_rounds.total_seconds(),
        )
    else:
        game.ended = True
        game.save()
        async_to_sync(channel_layer.group_send)(
            f"gameroom_{game_id}",
            {
                "type": "round.end",
                "round_number": round_number,
                "countdown_time": countdown_time,
            },
        )
