import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs

class GameManager:
    def __init__(self):
        # A dictionary of room names to TwoPlayerGame objects eg. {'room1': TwoPlayerGame, 'room2': TwoPlayerGame}
        self.games = {}

    def get_game(self, room_name):
        if room_name not in self.games:
            self.games[room_name] = TwoPlayerGame(room_name)
        return self.games[room_name]

class TwoPlayerGame:
    def __init__(self, room_name):
        # The name of the room eg. 'room1'
        self.room_name = room_name
        # The name of the group eg. 'pong_room1'
        self.room_group_name = f"pong_{room_name}"
        # A list of tuples of the form (channel_name, username) eg. [('channel1', 'user1'), ('channel2', 'user2')]
        self.players = []
        self.button_pressed = False

    def add_player(self, player_channel_name, player_username):
        self.players.append((player_channel_name, player_username))

    def remove_player(self, player_channel_name):
        self.players = [(ch, un) for ch, un in self.players if ch != player_channel_name]

    def get_opponent_channel(self, player_channel_name):
        for channel_name, _ in self.players:
            if channel_name != player_channel_name:
                return channel_name

    def press_button(self, player_channel_name):
        if not self.button_pressed:
            self.button_pressed = True
            return True
        return False

class PongConsumer(AsyncWebsocketConsumer):
    game_manager = GameManager()

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.username = None

        # Extract the username from the query parameters
        query_string = self.scope['query_string'].decode('utf-8')
        query_params = parse_qs(query_string)
        self.username = query_params.get('username', [f"User_{self.channel_name}"])[0]

        # Join the room group
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        # Add the player to the game
        game = self.game_manager.get_game(self.room_name)
        game.add_player(self.channel_name, self.username)

        # Send a message to the group notifying that a new client has joined
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': f"{self.username} has joined the room."
            }
        )

        # Accept the connection
        await self.accept()

    async def disconnect(self, close_code):
        # Remove the player from the game
        game = self.game_manager.get_game(self.room_name)
        game.remove_player(self.channel_name)

        # Send a message to the group notifying that a player has left
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': f"{self.username} has left the room."
            }
        )

        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle incoming messages
        message = json.loads(text_data)

        # Check if the message is a button press
        if message.get('type') == 'button.press':
            await self.handle_button_press()
        if message.get('type') == 'disconnect':
            await self.disconnect(message.get('close_code'))

    async def handle_button_press(self):
        # Get the game for the current room
        game = self.game_manager.get_game(self.room_name)

        # Press the button for the current player
        if game.press_button(self.channel_name):
            # If the button is pressed, get the opponent's channel
            opponent_channel = game.get_opponent_channel(self.channel_name)

            # Disconnect the current player
            await self.disconnect(close_code=1000)

            # Send a message to the opponent
            await self.channel_layer.send(
                opponent_channel,
                {
                    'type': 'chat.message',
                    'message': f"{self.username} pressed the button and wins!"
                }
            )

            # Disconnect the opponent
            await self.channel_layer.send(
                opponent_channel,
                {
                    'type': 'disconnect',
                    'close_code': 1000
                }
            )

    async def send_chat_message(self, message):
        # Send a message to the WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat.message',
            'message': message
        }))

    async def chat_message(self, event):
        # Send a chat message to the room group
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'chat.message',
            'message': message
        }))
