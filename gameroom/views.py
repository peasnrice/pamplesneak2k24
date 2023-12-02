from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from gameroom.models import Game, Player, Word
from users.models import CustomUser, UserProfile
from gameroom.forms import MessageSender, GameRoomForm
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib import messages
import random

# Initialize words list
def load_words():
    word_file = "/usr/share/dict/words"
    with open(word_file) as file:
        return file.read().splitlines()
    
WORDS = load_words()


# getActiveGames function now utilizes Django ORM efficiently
def getActiveGames():
    return Game.objects.filter(active=True).order_by('-created')

def pampleplay(request):
    games_list = getActiveGames()  # Fetch the list of active games
    context = {
        'games_list': games_list  # Pass the list of games to the template
    }
    return render(request, 'gameroom/play.html', context)

class GameInfo():
   def __init__(self, game_id, game_name, slug, active_players, max_players, word_bank_size, active):
      self.id = game_id
      self.game_name = game_name
      self.slug = slug
      self.active_players = active_players
      self.max_players = max_players
      self.word_bank_size = word_bank_size
      self.active = active

@login_required
def creategame(request):
    if request.method == 'POST':
        form = GameRoomForm(request.POST)
        if form.is_valid():
            save_game = form.save(commit=False)
            save_game.active = True
            save_game.save()
            # Redirect directly to the play view
            return redirect('gameroom:pampleplay')
    else:
        form = GameRoomForm()
    return render(request, 'gameroom/create.html', {'form': form})

@login_required
@never_cache
def joingame(request, game_id, slug):
    game = get_object_or_404(Game, pk=game_id)
    user = request.user

    word_list = random.sample(WORDS, min(len(WORDS), game.word_bank_size))

    # Creating or retrieving the player
    player, created = Player.objects.get_or_create(
        game=game, user=user, defaults={'name': user.username}
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

    game_words = Word.objects.filter(game=game_id).filter(send_to=player).order_by('created')
    player_word = ""
    if not game_words:
        player_word = ""
    else:
        player_word = game_words[0].word
        if game_words[0].created_by:
            sender = game_words[0].created_by

    context = {
        'form': form,
        'word': random.choice(WORDS),
        'word_list': word_list,
        'word_bank_size': game.word_bank_size,
        'game': game,
        'player': player,
        'players': all_players_query.order_by('-succesful_sneaks'),
        'player_count': players_query.count(),
        'player_word': player_word
    }

    return render(request, 'gameroom/ingame.html', context)

@login_required
def send_word(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    player, created = Player.objects.get_or_create(
        game=game, user=request.user, defaults={'name': request.user.username}
    )

    players_query = Player.objects.filter(game=game).exclude(id=player.id)
    players_dict = {p.id: p.name for p in players_query}

    if request.method == 'POST':
        form = MessageSender(players_dict, request.POST)
        if form.is_valid():
            # Process the form data and create a Word object
            word = form.cleaned_data['word']
            to_player_id = form.cleaned_data['target']
            to_player = Player.objects.get(id=to_player_id)
            created_by = None if form.cleaned_data['send_anonymously'] else player

            Word.objects.create(
                word=word, 
                player=player, 
                game=game, 
                send_to=to_player, 
                created_by=created_by
            )

            messages.success(request, 'Message successfully sent!')
        
            return redirect('gameroom:joingame', game_id=game_id, slug=game.slug)
    else:
        form = MessageSender(players_dict)

    context = {
        'form': form,
        'game': game,
    }

    return render(request, 'gameroom/ingame.html', context)

def refresh_word(request, game_id, player_id):
    game_words = Word.objects.filter(game=game_id, send_to=player_id).order_by('created')
    player_word = game_words[0].word if game_words else ""
    sender = game_words[0].created_by.name if game_words and game_words[0].created_by else "anonymous"

    html = render_to_string('gameroom/playerword.html', {'player_word': player_word, 'sender': sender})
    return JsonResponse({'html': html})