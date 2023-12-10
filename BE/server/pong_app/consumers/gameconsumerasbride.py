import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from pong_app.python_pong.Player import Player
from pong_app.python_pong.Game import Game
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from icecream import ic


class GameConsumerAsBridge(AsyncWebsocketConsumer):
    list_of_players = {}
    list_of_observers = {}
    list_of_keyboard_inputs = {}
    list_of_games = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_object = None
        self.player = None
        self.match_players = []
        self.keyboard_inputs = {
            "{self.player_1_id} + up" : False,
            "{self.player_1_id} + down": False,
            "{self.player_2_id} + up": False,
            "{self.player_2_id} + down": False}
        self.keyboard = {}
        self.left_player = None
        self.right_player = None

        self.keyboard_lock = asyncio.Lock()


    @database_sync_to_async
    def get_match(self, match_id):
        from api.tournament.models import Match

        try:
            print(f'Getting match {match_id}')
            self.match_object = Match.objects.get(id=match_id)

        except Match.DoesNotExist:
            # Send message to client via JSON and close the connection
            self.send(text_data=json.dumps({
                'error': 'Match does not exist'
            }))
            self.close()

    @database_sync_to_async
    def get_user(self, player_id):
        from api.userauth.models import CustomUser as User

        try:
            print(f'Getting user {player_id}')
            self.client_object = User.objects.get(id=player_id)

        except User.DoesNotExist:
            # Send message to client via JSON and close the connection
            self.send(text_data=json.dumps({
                'error': 'Player does not exist'
            }))
            self.close()

        # leftPlayer=Player(name=self.player_1_id, binds=self.keyboard[self.client_id]),
        # rightPlayer=Player(name=self.player_2_id, binds=self.keyboard[self.client_id]),


    async def initialize_game(self):
        try:
            self.list_of_keyboard_inputs[self.match_id] = self.keyboard_inputs

            self.list_of_games[self.match_id] = None

            # Create the game
            game = Game(
                dictKeyboard=self.keyboard_inputs,
                leftPlayer=Player(name=self.player_1_id, binds={"up" : "{self.player_1_id} + up", "down":"{self.player_1_id} + down", "left":"xx","right":"xx"}),
                rightPlayer=Player(name=self.player_2_id, binds={"up" : "{self.player_2_id} + up", "down":"{self.player_2_id} + down", "left":"xx","right":"xx"}),
            )
            print(f'Trying to add game to index {self.match_id}')
            self.list_of_games[self.match_id] = game


            print(f'Successfully added game to index {self.match_id}')
        except Exception as e:
            print(f'Error during game initialization: {e}')

        try:
            # Start the game
            print(f'Starting game {self.match_id}')
            if self.list_of_games[self.match_id] and not self.list_of_games[self.match_id].isAlive():
                # Check if both players for this match are connected
                if self.client_id in self.list_of_players and self.player_1_id in self.list_of_players and self.player_2_id in self.list_of_players:
                    print(f'Sending start command to game {self.match_id}')
                    self.list_of_games[self.match_id].start()
                    asyncio.create_task(self.game_update())
                else:
                    print(f'Cannot start game. Both players for this match are not connected yet.')
        except Exception as e:
            print(f'Error during game start: {e}')


    async def connect(self):
        try:
            query_string = self.scope['query_string'].decode('utf-8')
            query_params = parse_qs(query_string)
            self.match_id = self.scope['url_route']['kwargs']['match_id']
            self.player_1_id = query_params.get('player_1_id', [None])[0]
            self.player_2_id = query_params.get('player_2_id', [None])[0]
            self.client_id = query_params.get('client_id', [None])[0]
            self.scorelimit = query_params.get('scorelimit', [None])[0]

            print(f'Connecting to match {self.match_id} with client {self.client_id}. Player 1: {self.player_1_id}. Player 2: {self.player_2_id}')

            await self.get_match(self.match_id)
            await self.get_user(self.client_id)

            print(f'Connected to match {self.match_id} with client {self.client_id}. Player 1: {self.player_1_id}. Player 2: {self.player_2_id}')

            # Check if the game has been initialized
            if not self.list_of_games.get(self.match_id):
                print(f'Initializing game {self.match_id}')
                await self.initialize_game()

            await self.accept()

            print(f'Accepted connection to match {self.match_id} with client {self.client_id}. Player 1: {self.player_1_id}. Player 2: {self.player_2_id}')

            # Check if client is a player or observer
            if self.client_id == self.player_1_id:
                print(f'Client {self.client_id} is player 1')
                self.keyboard[self.client_id] = {"up": f"{self.client_id} + up", "down": f"{self.client_id} + down", "left": "xx", "right": "xx"}

                self.player = self.list_of_games[self.match_id]._leftPlayer
                self.list_of_players[self.client_id] = self.client_object
                self.match_players.append(self.client_object)
                print(f'Player 1: {self.player}')
            elif self.client_id == self.player_2_id:
                print(f'Client {self.client_id} is player 2')
                self.keyboard[self.client_id] = {"up": f"{self.client_id} + up", "down": f"{self.client_id} + down", "left": "xx", "right": "xx"}

                self.player = self.list_of_games[self.match_id]._rightPlayer
                self.list_of_players[self.client_id] = self.client_object
                self.match_players.append(self.client_object)
                print(f'Player 2: {self.player}')
            else:
                # Add the observer to the list of observers
                print(f'Client {self.client_id} is an observer')
                self.list_of_observers[self.client_id] = self.client_object

            # Add client to the group
            await self.channel_layer.group_add(
                self.match_id,
                self.channel_name
            )

            # Send message to group
            await self.broadcast_to_group(self.match_id, 'player_list', {'user': str(self.scope['user']), 'path': self.scope['path']})


        except Exception as e:
            print(f'Error during connection: {e}')
            await self.close()


    async def broadcast_to_group(self, group_name, command, data):
        print(f'Channel Broadcasting {command} to group {group_name}')

        await self.channel_layer.group_send(
            group_name,
            {
                'type': 'broadcast',
                'command': command,
                'data': data
            })

    async def broadcast(self, event):
        # Send message to WebSocket
        command = event['command']
        data = event['data']
        print(f'Sending message to client {self.client_id} with data: {data}')
        await self.send(text_data=json.dumps({
            'type': command,
            'data': data
        }))


    async def disconnect(self, close_code):
        if self.player:
            del self.list_of_players[self.client_id]
            if self.list_of_games[self.match_id] and self.list_of_games[self.match_id].isAlive():
                self.list_of_games[self.match_id].stop()

            # Remove the player from the match_players list
            self.match_players.remove(self.client_object)

            # Send message to group
            await self.broadcast_to_group(self.match_id, 'player_list', list(self.list_of_players.keys()))

        elif self.client_id in self.list_of_observers:
            del self.list_of_observers[self.client_id]

    async def receive(self, text_data):
        data = json.loads(text_data)
        command = data.get('command')
        key_status = data.get('key_status')
        
        print(f'Received command: {command} with data: {data}')

        if command == 'player_list':
            await self.send(text_data=json.dumps({
                'type': 'player_list',
                'data': list(self.list_of_players.keys()),
            }))
              
        elif command == 'start_game':
            print(f'Starting game {self.match_id}')
            if self.list_of_games[self.match_id] and not self.list_of_games[self.match_id].isAlive():
                # Check if both players for this match are connected
                if self.client_id in self.list_of_players and self.player_1_id in self.list_of_players and self.player_2_id in self.list_of_players:
                    print(f'Sending start command to game {self.match_id}')
                    self.list_of_games[self.match_id].start()
                    asyncio.create_task(self.game_update())
                else:
                    print(f'Cannot start game. Both players for this match are not connected yet.')

        elif command == 'keyboard':
            if self.list_of_games[self.match_id] and self.list_of_games[self.match_id].isAlive() and self.player:
                if key_status == 'on_press':
                    key = data.get('key')
                    self.on_press(key)
                elif key_status == 'on_release':
                    key = data.get('key')
                    self.on_release(key)


        elif command == 'disconnect':
            if self.client_id in self.list_of_players:
                del self.list_of_players[self.client_id]
                if self.list_of_games.get(self.match_id) and self.list_of_games[self.match_id].isAlive():
                    self.list_of_games[self.match_id].stop()

                # Remove the player from the match_players list
                self.match_players.remove(self.client_object)

                # Send message to group
                await self.broadcast_to_group(self.match_id, 'player_list', list(self.list_of_players.keys()))

            elif self.client_id in self.list_of_observers:
                del self.list_of_observers[self.client_id]


    async def game_update(self):
        while self.list_of_games[self.match_id] and self.list_of_games[self.match_id].isAlive():
            print(f'Sending game update to group {self.match_id}')

            # Update paddle positions based on keyboard inputs
            left_paddle = self.list_of_games[self.match_id]._leftPaddle
            right_paddle = self.list_of_games[self.match_id]._rightPaddle

            left_paddle.updatePosition()
            right_paddle.updatePosition()

            # Send updated game state to the group
            await self.broadcast_to_group(self.match_id, 'game_update', self.list_of_games[self.match_id].reportScreen())

            try:
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                logging.debug("Game update task canceled.")
                break
            except Exception as e:
                logging.error(f"Error in game_update: {e}")

    def on_press(self, key):
        print(f'I am player {self.client_id}, my keyboard is {self.keyboard.get(str(self.client_id), {})} and the key is {key}')

        formatted_key = f'{key}.{self.client_id}'  # Adjust the key format
        print(f'Trying to update key {formatted_key} for match {self.match_id}')
        if self.match_id in self.keyboard_inputs and formatted_key in self.keyboard_inputs[self.match_id]:
            self.keyboard_inputs[self.match_id][formatted_key] = True
            print(f'Successfully updated key {formatted_key} for match {self.match_id}')
        else:
            print(f'Invalid match_id {self.match_id} or key {formatted_key}')

    def on_release(self, key):
        print(f'I am player {self.client_id}, my keyboard is {self.keyboard.get(str(self.client_id), {})} and the key is {key}')

        formatted_key = f'{key}.{self.client_id}'  # Adjust the key format
        print(f'Trying to update key {formatted_key} for match {self.match_id}')
        if self.match_id in self.keyboard_inputs and formatted_key in self.keyboard_inputs[self.match_id]:
            self.keyboard_inputs[self.match_id][formatted_key] = False
            print(f'Successfully updated key {formatted_key} for match {self.match_id}')
        else:
            print(f'Invalid match_id {self.match_id} or key {formatted_key}')
