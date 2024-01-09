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
def round_transition_state(game_id):
    # Set the round to the transition state
    game = Game.objects.get(id=game_id)
    current_round = game.current_round
    round = Round.objects.get(game=game, round_number=current_round)
    round.state = "Transition"
    round.save()
    countdown_time = round.transition_state_duration.total_seconds()

    # Notify clients of the transition state
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
    round.state = "Create"
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
    round.state = "Play"
    round.save()

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
