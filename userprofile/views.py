from django.shortcuts import render
from gameroom.models import Game, Player


def user_games(request):
    if request.user.is_authenticated:
        # Get all Player instances for the current user
        player_instances = Player.objects.filter(user=request.user)

        # Retrieve the corresponding Game instances
        signed_up_games = [player.game for player in player_instances]

        return render(request, "userprofiles/profile.html", {"games": signed_up_games})
    else:
        return render(request, "start.html")
