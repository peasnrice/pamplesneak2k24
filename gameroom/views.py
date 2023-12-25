from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from gameroom.models import Game, Player, Word, Vote, ExampleWord
from users.models import CustomUser, UserProfile
from gameroom.forms import MessageSender, CreateGameForm, JoinGameForm
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import random
import json
import traceback

# QR Code Generation imports
import qrcode
from PIL import Image
from io import BytesIO
from django.http import HttpResponse

from django.conf import settings


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
    if request.method == "POST":
        form = CreateGameForm(request.POST)
        if form.is_valid():
            save_game = form.save(commit=False)
            save_game.active = True
            save_game.save()

            # Auto-join the game creator as a player
            user = request.user
            player, created = Player.objects.get_or_create(
                game=save_game, user=user, defaults={"name": user.username}
            )

            # Assign the game to the user's profile (if you have such a mechanism)
            user_profile, _ = UserProfile.objects.get_or_create(user=user)
            user_profile.current_game = save_game
            user_profile.current_player = player
            user_profile.save()

            # Optionally, perform any other logic you need for a new player joining

            # Redirect to the game view (update with your actual view's name and parameters)
            return redirect(
                "gameroom:joingame", game_id=save_game.id, slug=save_game.slug
            )
    else:
        form = CreateGameForm()

    return render(request, "gameroom/create.html", {"form": form})


@login_required
@never_cache
def joingame(request, game_id, slug):
    game = get_object_or_404(Game, pk=game_id)
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

    all_players_query = Player.objects.filter(game=game)
    players_query = Player.objects.filter(game=game).exclude(id=player.id)
    players_dict = {p.id: p.name for p in players_query}
    form = MessageSender(players_dict)

    game_words = (
        Word.objects.filter(game=game_id)
        .filter(send_to=player)
        .filter(completed=False)
        .order_by("created")
    )
    if not game_words:
        player_word = None
    else:
        player_word = game_words[0]

    context = {
        "form": form,
        "word_bank_size": game.word_bank_size,
        "game": game,
        "player": player,
        "players": all_players_query.order_by("-succesful_sneaks"),
        "player_count": players_query.count(),
        "player_word": player_word,
        "range1_10": range(1, 11),
    }

    return render(request, "gameroom/ingame.html", context)


@login_required
@never_cache
def stats(request, game_id, slug):
    game = get_object_or_404(Game, pk=game_id)
    user = request.user
    player, created = Player.objects.get_or_create(
        game=game, user=user, defaults={"name": user.username}
    )

    all_players_query = Player.objects.filter(game=game).order_by("-succesful_sneaks")

    successful_sneaks = Word.objects.filter(game=game, successful=True).select_related(
        "player", "created_by"
    )

    failed_sneaks = Word.objects.filter(game=game, successful=False).select_related(
        "player", "created_by"
    )

    received_sneaks = Word.objects.filter(
        game=game,
    ).select_related("player", "created_by")

    context = {
        "players": all_players_query,
        "successful_sneaks": successful_sneaks,
        "failed_sneaks": failed_sneaks,
        "received_sneaks": received_sneaks,
        "user_id": request.user.id,
        "player": player,
        "game": game,
    }

    return render(request, "gameroom/ingamestats.html", context)


@login_required
def send_word(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    player, created = Player.objects.get_or_create(
        game=game, user=request.user, defaults={"name": request.user.username}
    )

    players_query = Player.objects.filter(game=game).exclude(id=player.id)
    players_dict = {p.id: p.name for p in players_query}

    if request.method == "POST":
        form = MessageSender(players_dict, request.POST)
        if form.is_valid():
            # Process the form data and create a Word object
            word = form.cleaned_data["word"]
            to_player_id = form.cleaned_data["target"]
            to_player = Player.objects.get(id=to_player_id)
            created_by = None if form.cleaned_data["send_anonymously"] else player

            Word.objects.create(
                word=word,
                player=player,
                game=game,
                send_to=to_player,
                created_by=created_by,
            )

            messages.success(request, "Message successfully sent!")

            return redirect("gameroom:joingame", game_id=game_id, slug=game.slug)
    else:
        form = MessageSender(players_dict)

    context = {
        "form": form,
        "game": game,
    }

    return render(request, "gameroom/ingame.html", context)


def refresh_word(request, game_id, player_id):
    game_words = Word.objects.filter(game=game_id, send_to=player_id).order_by(
        "created"
    )
    player_word = game_words[0].word if game_words else ""

    game = get_object_or_404(Game, pk=game_id)
    player = get_object_or_404(Player, pk=player_id)

    game_words = (
        Word.objects.filter(game=game_id)
        .filter(send_to=player)
        .filter(completed=False)
        .order_by("created")
    )
    number_of_words = game_words.count
    if not game_words:
        player_word = None
    else:
        player_word = game_words[0]

    context = {
        "player_word": player_word,
        "game": game,
        "player": player,
        "number_of_words": number_of_words,
        "range1_10": range(1, 11),
    }

    # You can now directly use game_word for the context
    render = render_to_string("gameroom/playerword.html", context, request=request)

    return JsonResponse({"html": render})


def word_success(request, word_id, game_id, player_id):
    game_word = Word.objects.get(id=word_id)
    # Perform the success logic here
    game_word.completed = True
    game_word.successful = True
    game_word.save()

    player = game_word.send_to
    player.succesful_sneaks = Word.objects.filter(
        send_to=player, successful=True
    ).count()
    player.save()

    game = get_object_or_404(Game, pk=game_id)

    game_words = (
        Word.objects.filter(game=game_id)
        .filter(send_to=player)
        .filter(completed=False)
        .order_by("created")
    )
    number_of_words = game_words.count
    if not game_words:
        player_word = None
    else:
        player_word = game_words[0]

    context = {
        "player_word": player_word,
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
    game_word.save()

    player = game_word.send_to
    player.failed_sneaks = Word.objects.filter(send_to=player, successful=False).count()
    player.save()

    game = get_object_or_404(Game, pk=game_id)

    game_words = (
        Word.objects.filter(game=game_id)
        .filter(send_to=player)
        .filter(completed=False)
        .order_by("created")
    )
    number_of_words = game_words.count
    if not game_words:
        player_word = None
    else:
        player_word = game_words[0]

    context = {
        "player_word": player_word,
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

    game_words = (
        Word.objects.filter(game=game_id)
        .filter(send_to=player)
        .filter(completed=False)
        .order_by("created")
    )
    number_of_words = game_words.count
    if not game_words:
        player_word = None
    else:
        player_word = game_words[0]

    context = {
        "player_word": player_word,
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


def validate_sneak(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    user = request.user
    player, created = Player.objects.get_or_create(
        game=game, user=user, defaults={"name": user.username}
    )
    data = json.loads(request.body)
    sneak_id = data.get("sneak_id")
    sneak = get_object_or_404(Word, id=sneak_id)

    vote, created = Vote.objects.get_or_create(
        word=sneak, player=player, defaults={"vote_type": "validate"}
    )
    vote.vote_type = "validate"
    vote.save()
    sneak = get_object_or_404(Word, id=sneak_id)

    if not created:
        print("vote note created")
    return JsonResponse(
        {
            "validations_count": sneak.validations_count,
            "rejections_count": sneak.rejections_count,
        }
    )


def reject_sneak(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    user = request.user
    player, created = Player.objects.get_or_create(
        game=game, user=user, defaults={"name": user.username}
    )

    data = json.loads(request.body)
    sneak_id = data.get("sneak_id")
    sneak = get_object_or_404(Word, id=sneak_id)

    vote, created = Vote.objects.get_or_create(
        word=sneak, player=player, defaults={"vote_type": "reject"}
    )
    vote.vote_type = "reject"
    vote.save()
    print(sneak.validations_count)
    sneak = get_object_or_404(Word, id=sneak_id)

    if not created:
        print("vote note created")

    return JsonResponse(
        {
            "validations_count": sneak.validations_count,
            "rejections_count": sneak.rejections_count,
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
    create_game_form = CreateGameForm()
    join_game_form = JoinGameForm(request.POST or None)

    storage = messages.get_messages(request)
    for message in storage:
        if "logged in" in message.message:
            storage.used = True

    if request.method == "POST":
        if join_game_form.is_valid():
            game_room_code = join_game_form.cleaned_data["game_room_code"]
            try:
                game = Game.objects.get(game_room_code=game_room_code)
                return redirect("gameroom:joingame", game_id=game.id, slug=game.slug)
            except Game.DoesNotExist:
                messages.error(request, "Game with this code does not exist.")
        else:
            # Redirect to homepage if form is invalid
            return redirect(
                "homepage_url_name"
            )  # Replace 'homepage_url_name' with the URL name of your homepage

    return render(
        request,
        "start.html",
        {"join_game": join_game_form, "create_game": create_game_form},
    )
