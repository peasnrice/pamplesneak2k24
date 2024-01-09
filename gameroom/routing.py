# routing.py
from django.urls import path
from .consumers import GameRoomConsumer

websocket_urlpatterns = [
    path("ws/gameroom/<int:game_id>/", GameRoomConsumer.as_asgi()),
]
