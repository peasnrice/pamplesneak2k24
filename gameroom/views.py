from datetime import timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from gameroom.models import Game, Round, Player, Word, Vote, ExampleWord, Like
from users.models import UserProfile
from gameroom.forms import (
    MessageSender,
    CreateGameForm,
    RoundForm,
    JoinGameForm,
    StartGameForm,
)
from django.forms import formset_factory
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .tasks import send_game_start_message, round_transition_state
import random
import json
import traceback
from django.urls import reverse

# QR Code Generation imports
import qrcode
from io import BytesIO
from django.http import HttpResponse
from django.utils import timezone


from rest_framework.decorators import api_view
from rest_framework.response import Response
from gameroom.utilities import send_push_notification


# getActiveGames function now utilizes Django ORM efficiently
def getActiveGames():
    return Game.objects.filter(active=True).order_by("-created")


def pampleplay(request):
    games_list = getActiveGames()  # Fetch the list of active games
    context = {"games_list": games_list}  # Pass the list of games to the template
    return render(request, "gameroom/play.html", context)


class GameInfo:
    def __init__(
        self,
        game_id,
        game_name,
        slug,
        active_players,
        max_players,
        word_bank_size,
        active,
    ):
        self.id = game_id
        self.game_name = game_name
        self.slug = slug
        self.active_players = active_players
        self.max_players = max_players
        self.word_bank_size = word_bank_size
        self.active = active


@login_required
def creategame(request):
    RoundFormSet = formset_factory(RoundForm, extra=0)

    if request.method == "POST":
        form = CreateGameForm(request.POST)
        round_formset = RoundFormSet(request.POST)

        if form.is_valid() and round_formset.is_valid():
            save_game = form.save(commit=False)
            save_game.active = True
            save_game.save()

            # Saving each round
            for round_form in round_formset:
                round_instance = round_form.save(commit=False)
                round_instance.game = save_game
                round_instance.save()

            # Auto-join the game creator as a player
            user = request.user
            player, created = Player.objects.get_or_create(
                game=save_game, user=user, defaults={"name": user.username}
            )

            # Assign the game to the user's profile
            user_profile, _ = UserProfile.objects.get_or_create(user=user)
            user_profile.current_game = save_game
            user_profile.current_player = player
            user_profile.save()

            # Redirect to the game view
            return redirect(
                "gameroom:joingame", game_id=save_game.id, slug=save_game.slug
            )
    else:
        form = CreateGameForm()
        round_formset = RoundFormSet()

    return render(
        request, "gameroom/create.html", {"form": form, "round_formset": round_formset}
    )


@login_required
@never_cache
def joingame(request, game_id, slug):
    game = get_object_or_404(Game, pk=game_id)

    current_round = Round.objects.get(game=game, round_number=game.current_round)
    user = request.user

    # Creating or retrieving the player
    player, created = Player.objects.get_or_create(
        game=game, user=user, defaults={"name": user.username}
    )

    # Handling UserProfile
    user_profile, _ = UserProfile.objects.get_or_create(user=user)

    # Assigning the current game to UserProfile
    user_profile.current_game = game
    user_profile.current_player = player
    user_profile.save()

    # Update the number of players
    game.number_of_players = Player.objects.filter(game=game).count()
    game.save()

    if game.active == False:
        return redirect("gameroom:lobby", game_id=game_id, slug=game.slug)

    all_players_query = Player.objects.filter(game=game)
    players_query = Player.objects.filter(game=game).exclude(id=player.id)
    players_dict = {p.id: p.name for p in players_query}

    hide_target = current_round.state == "create" or current_round.state == "transition"
    form = MessageSender(players_dict, hide_target=hide_target)

    words_submitted_this_round = Word.objects.filter(
        player=player, round=current_round
    ).count()

    # determine sneaks sent star count
    can_submit_more = words_submitted_this_round < current_round.sneaks_per_round
    # no_limits == true allows for any number of sneaks to be sent at the beginning of a round
    no_limits = False

    # unlimited_sneaks == true allows users to send additioanl sneaks while the round is in progress, otherwise sneaks are limited to between rounds.
    allow_additional_sneaks = current_round.allow_additional_sneaks
    if current_round.sneaks_per_round == 0:
        no_limits = True
        can_submit_more = True
        sneak_stars = words_submitted_this_round + 1
    else:
        sneak_stars = current_round.sneaks_per_round

    # Query to get the words associated with the player and game, not completed
    player_words = (
        Word.objects.filter(game=game_id)
        .filter(send_to=player)
        .filter(completed=False)
        .order_by("created")
    )

    # Get the count of words
    number_of_words = player_words.count()

    # Select the first word or None if the list is empty
    current_player_word = player_words[0] if player_words else None

    # Calculate the total sneaks allowed (assuming sneaks_range is a list or similar iterable)
    total_sneaks = sneak_stars

    # Calculate remaining sneaks
    remaining_sneaks = sneak_stars - words_submitted_this_round

    remaining_time = current_round.get_remaining_time()
    print(current_round)
    print(current_round.round_number)
    print("remaining time")
    print(current_round.state)
    print(current_round.state_start_time)
    print(remaining_time)

    context = {
        "form": form,
        "word_bank_size": game.word_bank_size,
        "game": game,
        "player": player,
        "players": all_players_query.order_by("-succesful_sneaks"),
        "player_count": players_query.count(),
        "number_of_words": number_of_words,
        "player_word": current_player_word,
        "player_words": player_words,
        "range1_10": range(1, 11),
        "current_round": current_round,
        "can_submit_more": can_submit_more,
        "words_submitted_this_round": words_submitted_this_round,
        "remaining_time": remaining_time,
        "sneaks_range": range(1, sneak_stars + 1),
        "no_limits": no_limits,
        "allow_additional_sneaks": allow_additional_sneaks,
        "hide_target": hide_target,
        "remaining_sneaks": remaining_sneaks,
    }

    return render(request, "gameroom/ingame.html", context)


@login_required
@never_cache
def timeline(request, game_id, slug):
    game = get_object_or_404(Game, pk=game_id)
    current_round = Round.objects.get(game=game, round_number=game.current_round)
    user = request.user
    player, created = Player.objects.get_or_create(
        game=game, user=user, defaults={"name": user.username}
    )

    all_players_query = Player.objects.filter(game=game).order_by("-succesful_sneaks")

    all_sneaks = Word.objects.filter(
        game=game,
        completed=True,
    ).order_by("-time_completed")

    successful_sneaks = (
        Word.objects.filter(game=game, completed=True, successful=True)
        .select_related("player", "created_by")
        .order_by("-created")
    )

    failed_sneaks = (
        Word.objects.filter(game=game, completed=True, successful=False, skipped=False)
        .select_related("player", "created_by")
        .order_by("-created")
    )

    skipped_sneaks = (
        Word.objects.filter(game=game, completed=True, skipped=True)
        .select_related("player", "created_by")
        .order_by("-created")
    )

    received_sneaks = Word.objects.filter(
        game=game,
    ).select_related("player", "created_by")

    context = {
        "players": all_players_query,
        "all_sneaks": all_sneaks,
        "successful_sneaks": successful_sneaks,
        "failed_sneaks": failed_sneaks,
        "skipped_sneaks": skipped_sneaks,
        "received_sneaks": received_sneaks,
        "user_id": request.user.id,
        "player": player,
        "game": game,
        "current_round": current_round,
        "remaining_time": current_round.get_remaining_time(),
    }

    return render(request, "gameroom/timeline.html", context)


@login_required
@never_cache
def leaderboard(request, game_id, slug):
    game = get_object_or_404(Game, pk=game_id)
    current_round = Round.objects.get(game=game, round_number=game.current_round)
    user = request.user
    player, created = Player.objects.get_or_create(
        game=game, user=user, defaults={"name": user.username}
    )

    all_players_query = Player.objects.filter(game=game).order_by("-succesful_sneaks")

    all_sneaks = Word.objects.filter(game=game).order_by("-created")

    successful_sneaks = (
        Word.objects.filter(game=game, successful=True)
        .select_related("player", "created_by")
        .order_by("-created")
    )

    failed_sneaks = (
        Word.objects.filter(game=game, successful=False, skipped=False)
        .select_related("player", "created_by")
        .order_by("-created")
    )

    skipped_sneaks = (
        Word.objects.filter(game=game, skipped=True)
        .select_related("player", "created_by")
        .order_by("-created")
    )

    received_sneaks = Word.objects.filter(
        game=game,
    ).select_related("player", "created_by")

    context = {
        "players": all_players_query,
        "all_sneaks": all_sneaks,
        "successful_sneaks": successful_sneaks,
        "failed_sneaks": failed_sneaks,
        "skipped_sneaks": skipped_sneaks,
        "received_sneaks": received_sneaks,
        "user_id": request.user.id,
        "player": player,
        "game": game,
        "current_round": current_round,
        "remaining_time": current_round.get_remaining_time(),
    }

    return render(request, "gameroom/leaderboard.html", context)


@login_required
def send_word(request, game_id, round_id):
    game = get_object_or_404(Game, pk=game_id)
    current_round = get_object_or_404(
        Round, pk=round_id, game=game
    )  # Retrieve the round

    player, created = Player.objects.get_or_create(
        game=game, user=request.user, defaults={"name": request.user.username}
    )

    players_query = Player.objects.filter(game=game).exclude(id=player.id)
    players_dict = {p.id: p.name for p in players_query}

    words_submitted_this_round = Word.objects.filter(
        player=player, round=current_round
    ).count()

    can_submit_more = words_submitted_this_round < current_round.sneaks_per_round

    if request.method == "POST":
        hide_target = (
            current_round.state == "create" or current_round.state == "transition"
        )
        form = MessageSender(players_dict, request.POST, hide_target=hide_target)
        if form.is_valid():
            # Process the form data and create a Word object
            word = form.cleaned_data["word"]
            to_player_id = form.cleaned_data.get("target")

            if to_player_id:
                try:
                    to_player = Player.objects.get(id=to_player_id)
                except Player.DoesNotExist:
                    # Handle the case where the player does not exist
                    to_player = None
            else:
                to_player = None

            created_by = None if form.cleaned_data["send_anonymously"] else player

            Word.objects.create(
                word=word,
                player=player,
                game=game,
                send_to=to_player,
                created_by=created_by,
                round=current_round,
            )

            if to_player:
                game_slug = game.slug
                game_url = reverse("gameroom:joingame", args=[game_id, game_slug])
                notification_payload = {
                    "title": "New Sneak",
                    "message": "You've received a new sneak! Check it out.",
                    "url": game_url,
                }
                send_push_notification.delay(to_player.user.id, notification_payload)

            messages.success(request, "Message successfully sent!")

            return redirect("gameroom:joingame", game_id=game_id, slug=game.slug)
        else:
            print("form errros:")
            print(form.errors)
    else:
        hide_target = (
            current_round.state == "create" or current_round.state == "transition"
        )
        form = MessageSender(players_dict, hide_target=hide_target)

    context = {
        "form": form,
        "game": game,
        "player": player,
        "current_round": current_round,
        "can_submit_more": can_submit_more,
        "words_submitted_this_round": words_submitted_this_round,
        "remaining_time": current_round.get_remaining_time(),
    }

    return render(request, "gameroom/ingame.html", context)


def refresh_word(request, game_id, player_id):
    game = get_object_or_404(Game, pk=game_id)
    player = get_object_or_404(Player, pk=player_id)

    # Query to get the words associated with the player and game, not completed
    player_words = (
        Word.objects.filter(game=game_id)
        .filter(send_to=player)
        .filter(completed=False)
        .order_by("created")
    )

    # Get the count of words
    number_of_words = player_words.count()

    # Select the first word or None if the list is empty
    current_player_word = player_words[0] if player_words else None

    context = {
        "player_word": current_player_word,  # The current word to display
        "player_words": player_words,  # List of all words for the player
        "game": game,
        "player": player,
        "number_of_words": number_of_words,
        "range1_10": range(1, 11),
    }

    # Render the template with the context
    render = render_to_string("gameroom/playerword.html", context, request=request)

    return JsonResponse({"html": render})


def word_success(request, word_id, game_id, player_id):

    print("word_id")
    print(word_id)

    game_word = Word.objects.get(id=word_id)
    # Perform the success logic here
    game_word.completed = True
    game_word.successful = True
    game_word.skipped = False
    game_word.time_completed = timezone.now()
    game_word.save()

    player = game_word.send_to
    player.succesful_sneaks = Word.objects.filter(
        send_to=player, successful=True
    ).count()
    player.save()

    game = get_object_or_404(Game, pk=game_id)

    player_words = (
        Word.objects.filter(game=game_id)
        .filter(send_to=player)
        .filter(completed=False)
        .order_by("created")
    )
    number_of_words = player_words.count()

    current_player_word = player_words[0] if player_words else None

    context = {
        "player_word": current_player_word,  # The current word to display
        "player_words": player_words,  # List of all words for the player
        "game": game,
        "player": player,
        "number_of_words": number_of_words,
        "range1_10": range(1, 11),
    }

    # You can now directly use game_word for the context
    render = render_to_string("gameroom/playerword.html", context, request=request)

    return JsonResponse({"html": render})


def word_fail(request, word_id, game_id, player_id):
    game_word = Word.objects.get(id=word_id)
    # Perform the success logic here
    game_word.completed = True
    game_word.successful = False
    game_word.skipped = False
    game_word.save()

    player = game_word.send_to
    player.failed_sneaks = Word.objects.filter(send_to=player, successful=False).count()
    player.save()

    game = get_object_or_404(Game, pk=game_id)

    player_words = (
        Word.objects.filter(game=game_id)
        .filter(send_to=player)
        .filter(completed=False)
        .order_by("created")
    )
    number_of_words = player_words.count()

    current_player_word = player_words[0] if player_words else None

    context = {
        "player_word": current_player_word,  # The current word to display
        "player_words": player_words,  # List of all words for the player
        "game": game,
        "player": player,
        "number_of_words": number_of_words,
        "range1_10": range(1, 11),
    }

    # You can now directly use game_word for the context
    render = render_to_string("gameroom/playerword.html", context, request=request)

    return JsonResponse({"html": render})


def word_skip(request, word_id, game_id, player_id):
    game_word = Word.objects.get(id=word_id)
    # Perform the success logic here
    game_word.completed = True
    game_word.successful = False
    game_word.skipped = True
    game_word.save()

    player = game_word.send_to
    player.failed_sneaks = Word.objects.filter(send_to=player, successful=False).count()
    player.save()

    game = get_object_or_404(Game, pk=game_id)

    player_words = (
        Word.objects.filter(game=game_id)
        .filter(send_to=player)
        .filter(completed=False)
        .order_by("created")
    )
    number_of_words = player_words.count()

    current_player_word = player_words[0] if player_words else None

    context = {
        "player_word": current_player_word,  # The current word to display
        "player_words": player_words,  # List of all words for the player
        "game": game,
        "player": player,
        "number_of_words": number_of_words,
        "range1_10": range(1, 11),
    }

    # You can now directly use game_word for the context
    render = render_to_string("gameroom/playerword.html", context, request=request)

    return JsonResponse({"html": render})


@csrf_exempt
@require_http_methods(["POST"])
def get_inspiration(request):
    try:
        example_words = ExampleWord.objects.all()
        if example_words.exists():
            random_word = random.choice(example_words)
            # Check if there's a note and append it
            if random_word.note:
                response_text = f"{random_word.word} - {random_word.note}"
            else:
                response_text = random_word.word
            return JsonResponse({"response_text": response_text})
        else:
            return JsonResponse({"response_text": "No words available."})
    except Exception as e:
        traceback.print_exc()  # Print full traceback
        return JsonResponse({"error": str(e)}, status=500)


@require_POST
def validate_sneak(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    user = request.user
    player, created = Player.objects.get_or_create(
        game=game, user=user, defaults={"name": user.username}
    )
    data = json.loads(request.body)
    sneak_id = data.get("sneak_id")
    sneak = get_object_or_404(Word, id=sneak_id)

    # Check if a validate vote already exists
    existing_vote = Vote.objects.filter(word=sneak, player=player).first()

    if existing_vote and existing_vote.vote_type == "validate":
        # If a validate vote exists, remove it to undo the validation
        existing_vote.delete()
        validated = False
    else:
        # If no validate vote exists or a reject vote exists, change to validate
        Vote.objects.update_or_create(
            word=sneak, player=player, defaults={"vote_type": "validate"}
        )
        validated = True

    # Update counts after modification
    sneak.validations_count = Vote.objects.filter(
        word=sneak, vote_type="validate"
    ).count()
    sneak.rejections_count = Vote.objects.filter(word=sneak, vote_type="reject").count()
    sneak.save()

    return JsonResponse(
        {
            "validations_count": sneak.validations_count,
            "rejections_count": sneak.rejections_count,
            "validated": validated,
        }
    )


@require_POST
def reject_sneak(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    user = request.user
    player, created = Player.objects.get_or_create(
        game=game, user=user, defaults={"name": user.username}
    )
    data = json.loads(request.body)
    sneak_id = data.get("sneak_id")
    sneak = get_object_or_404(Word, id=sneak_id)

    # Check if a reject vote already exists
    existing_vote = Vote.objects.filter(word=sneak, player=player).first()

    if existing_vote and existing_vote.vote_type == "reject":
        # If a reject vote exists, remove it to undo the rejection
        existing_vote.delete()
        rejected = False
    else:
        # If no reject vote exists or a validate vote exists, change to reject
        Vote.objects.update_or_create(
            word=sneak, player=player, defaults={"vote_type": "reject"}
        )
        rejected = True

    # Update counts after modification
    sneak.validations_count = Vote.objects.filter(
        word=sneak, vote_type="validate"
    ).count()
    sneak.rejections_count = Vote.objects.filter(word=sneak, vote_type="reject").count()
    sneak.save()

    return JsonResponse(
        {
            "validations_count": sneak.validations_count,
            "rejections_count": sneak.rejections_count,
            "rejected": rejected,
        }
    )


@require_POST
def like_sneak(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    user = request.user
    player, created = Player.objects.get_or_create(
        game=game, user=user, defaults={"name": user.username}
    )
    data = json.loads(request.body)
    sneak_id = data.get("sneak_id")
    sneak = get_object_or_404(Word, id=sneak_id)

    # Check if a like already exists
    like_exists = Like.objects.filter(word=sneak, player=player).exists()

    if like_exists:
        # If a like exists, unlike (remove the like)
        Like.objects.filter(word=sneak, player=player).delete()
        liked = False  # Indicate that the user has unliked the word
    else:
        # If no like exists, add a new like
        Like.objects.create(word=sneak, player=player)
        liked = True  # Indicate that the user has liked the word

    sneak.likes_count = sneak.likes.all().count()
    sneak.save()

    if created:
        # If a new like was successfully added, update the like count on the Word model
        sneak.likes_count = sneak.likes.all().count()
        sneak.save()

    return JsonResponse(
        {
            "validations_count": sneak.validations_count,
            "rejections_count": sneak.rejections_count,
            "likes_count": sneak.likes_count,
        }
    )


def qr_code_view(request, game_id, slug):
    # Construct your game room URL based on the game_id
    game_room_url = f"http://pamplesneak.fly.dev/gameroom/pampleplay/{game_id}/{slug}"
    qr_image = generate_qr_code(game_room_url)
    return HttpResponse(qr_image, content_type="image/png")


def generate_qr_code(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_io = BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)
    return img_io


@login_required
def joingame2(request):
    user = request.user
    create_game_form = (
        CreateGameForm(request.POST or None)
        if request.method == "POST" and "create_game" in request.POST
        else CreateGameForm()
    )
    join_game_form = (
        JoinGameForm(request.POST or None)
        if request.method == "POST" and "join_game" in request.POST
        else JoinGameForm()
    )

    if request.method == "POST":
        # Handling game creation
        if "create_game" in request.POST and create_game_form.is_valid():
            new_game = create_game_form.save()
            new_game.host = request.user
            new_game.save()

            # Convert values to timedelta objects
            create_state_duration = timedelta(
                minutes=int(create_game_form.cleaned_data["create_state_duration"])
            )
            play_state_duration = timedelta(
                minutes=int(create_game_form.cleaned_data["play_state_duration"])
            )

            for i in range(1, new_game.number_of_rounds + 1):
                Round.objects.create(
                    game=new_game,
                    round_number=i,
                    play_state_duration=play_state_duration,
                    sneaks_per_round=create_game_form.cleaned_data["sneaks_per_round"],
                    allow_additional_sneaks=create_game_form.cleaned_data[
                        "allow_additional_sneaks"
                    ],
                    create_state_duration=create_state_duration,
                )

            player, created = Player.objects.get_or_create(
                game=new_game,
                user=request.user,
                defaults={"name": request.user.username},
            )
            # Redirect to the game room or another appropriate page after creating the game
            return redirect("gameroom:lobby", game_id=new_game.id, slug=new_game.slug)

        # Handling joining a game
        if "join_game" in request.POST and join_game_form.is_valid():
            game_room_code = join_game_form.cleaned_data["game_room_code"]
            try:
                game = Game.objects.get(game_room_code=game_room_code)
                # Creating or retrieving the player
                player, created = Player.objects.get_or_create(
                    game=game, user=user, defaults={"name": user.username}
                )

                # Handling UserProfile
                user_profile, _ = UserProfile.objects.get_or_create(user=user)

                # Assigning the current game to UserProfile
                user_profile.current_game = game
                user_profile.current_player = player
                user_profile.save()

                # Update the number of players
                game.number_of_players = Player.objects.filter(game=game).count()
                game.save()
                return redirect("gameroom:lobby", game_id=game.id, slug=game.slug)
            except Game.DoesNotExist:
                messages.error(request, "Game with this code does not exist.")

    # Handling non-POST requests or invalid form submissions
    return render(
        request,
        "start.html",
        {
            "join_game": join_game_form,
            "create_game": create_game_form,
        },
    )


@login_required
def game_lobby(request, game_id, slug):
    game = get_object_or_404(Game, id=game_id, slug=slug)
    user = request.user
    player, created = Player.objects.get_or_create(
        game=game, user=user, defaults={"name": user.username}
    )

    if game.active == True:
        return redirect("gameroom:joingame", game_id=game_id, slug=game.slug)

    players = Player.objects.filter(game=game)
    user_is_host = game.host == user

    if request.method == "POST":
        start_game_form = StartGameForm(request.POST)
        if start_game_form.is_valid() and user_is_host:
            game.active = True
            game.save()
            send_game_start_message.delay(game_id)
            round_transition_state.delay(game_id)
            return redirect("gameroom:joingame", game_id=game_id, slug=game.slug)
    else:
        start_game_form = StartGameForm()

    return render(
        request,
        "gameroom/lobby.html",
        {
            "game": game,
            "players": players,
            "user_is_host": user_is_host,
            "start_game_form": start_game_form,
            "player": player,
        },
    )


# Desktop App API


# Create Game
@api_view(["POST"])
def create_game(request):
    game_name = request.data.get("game_name")
    new_game = Game(game_name=game_name)
    new_game.save()
    return Response({"message": "Game created", "game_id": new_game.id})
