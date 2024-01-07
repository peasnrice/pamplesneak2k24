# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Player
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
                Player.objects.filter(game_id=self.game_id).values_list(
                    "name", flat=True
                )
            )
        )()
        await self.channel_layer.group_send(
            self.game_group_name, {"type": "update_players", "players": players}
        )

    # Receive message from room group
    async def game_room_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

    async def game_start(self, event):
        # Handle the game start message
        await self.send(event["text"])

    async def round_start(self, event):
        await self.send_json(
            {
                "type": "round.start",
                "round_number": event["round_number"],
                "game_state": "create",
                "countdown_time": event["countdown_time"],
            }
        )

    async def round_end(self, event):
        await self.send_json(
            {
                "type": "round.end",
                "round_number": event["round_number"],
                "game_state": "play",
                "countdown_time": event["countdown_time"],
            }
        )

    async def game_end(self, event):
        await self.send_json(
            {
                "type": "game.end",
            }
        )
