from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from gameroom.forms import GameRoomForm, MessageSender
import random

def pampleplay(request):
    # Prepare your context if needed
    context = {}  # Replace with your actual context data

    return render(request, 'gameroom/play.html', context)

@login_required
def creategame(request):
    if request.method == 'POST':
        form = GameRoomForm(request.POST)
        if form.is_valid():
            save_game = form.save(commit=False)
            save_game.active = True
            save_game.save()
            games_list = getActiveGames()
            return redirect('pamplesneak_play', {  # Adjust the redirect as needed
                'games_list': games_list,
                'word': random.choice(WORDS),
            })
    else:
        form = GameRoomForm()
    return render(request, 'gameroom/create.html', {'form': form})