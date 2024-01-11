# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Player, Game
import json


class GameRoomConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope["url_route"]["kwargs"]["game_id"]
        self.game_group_name = "gameroom_%s" % self.game_id

        # Joining the room group
        await self.channel_layer.group_add(self.game_group_name, self.channel_name)

        await self.broadcast_players()
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.broadcast_players()
        await self.channel_layer.group_discard(self.game_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.game_group_name, {"type": "game_room_message", "message": message}
        )

    # Custom handler for updating players
    async def update_players(self, event):
        players = event["players"]
        await self.send(text_data=json.dumps({"players": players}))

    async def broadcast_players(self):
        # Fetch updated list of players asynchronously
        players = await sync_to_async(
            lambda: list(
                Player.objects.filter(game_id=self.game_id).select_related("user")
            )
        )()

        # Fetch the host of the game
        host = await sync_to_async(lambda: Game.objects.get(id=self.game_id).host)()

        # Prepare player data
        player_data = await sync_to_async(
            lambda: [
                {"name": player.name, "is_host": player.user == host}
                for player in players
            ]
        )()

        # Send the player data
        await self.channel_layer.group_send(
            self.game_group_name, {"type": "update_players", "players": player_data}
        )

    # Receive message from room group
    async def game_room_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

    async def game_start(self, event):
        # Handle the game start message
        await self.send(event["text"])

    async def round_transition(self, event):
        await self.send_json(
            {
                "type": "round.transition",
                "round_number": event["round_number"],
                "round_state": event["round_state"],
                "countdown_time": event["countdown_time"],
            }
        )

    async def round_create(self, event):
        await self.send_json(
            {
                "type": "round.create",
                "round_number": event["round_number"],
                "round_state": event["round_state"],
                "countdown_time": event["countdown_time"],
            }
        )

    async def round_play(self, event):
        await self.send_json(
            {
                "type": "round.play",
                "round_number": event["round_number"],
                "round_state": event["round_state"],
                "countdown_time": event["countdown_time"],
            }
        )

    async def game_end(self, event):
        await self.send_json(
            {
                "type": "game.end",
            }
        )
