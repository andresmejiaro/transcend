import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from ws_api.python_pong.Player import Player
from ws_api.python_pong.Game import Game
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.utils import timezone
# Icecream is a library that allows us to ic variables in a more readable way its is only for debugging and can be removed
from icecream import ic


class GameConsumerAsBridge(AsyncWebsocketConsumer):
    list_of_players = {}            # Holds the model objects of the players in all matches
    list_of_observers = {}          # Holds the model objects of the observers in all matches
    list_of_keyboard_inputs = {}    # Holds the keyboard inputs for each match (eg. self.list_of_keyboard_inputs[self.match_id] = {"up.1": False, "down.1": False, "up.2": False, "down.2": False})
    list_of_games = {}              # Holds the Game objects for each match (eg. self.list_of_games[self.match_id] = Game(...))


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_object = None   # Holds the model object of the client
        self.keyboard = {}          # Holds the keyboard inputs for each player (eg. self.keyboard[self.player_1_id] = {"up": f"up.{self.player_1_id}", "down": f"down.{self.player_1_id}", "left": "xx", "right": "xx"})
        self.left_player = None     # Holds the Player object for the left player for the game
        self.right_player = None    # Holds the Player object for the right player for the game
        self.player_1_score = 0
        self.player_2_score = 0



    @database_sync_to_async
    def get_match(self, match_id):
        # We import the model here to avoid circular imports and allow the consumer to be imported in the routing.py file
        from api.tournament.models import Match

        try:
            ic(f'Getting match {match_id}')
            self.match_object = Match.objects.get(pk=match_id)
            ic(f'The match object is {self.match_object}')

        except Exception as e:
            ic(f'Error during match retrieval: {e}')
            # Send message to client via JSON and close the connection
            self.send(text_data=json.dumps({
                'error': 'Match does not exist'
            }))
            self.close()

    @database_sync_to_async
    def get_user(self, player_id):
        # We import the model here to avoid circular imports and allow the consumer to be imported in the routing.py file
        from api.userauth.models import CustomUser as User

        try:
            ic(f'Getting user {player_id}')
            self.client_object = User.objects.get(pk=player_id)
            ic(f'The user object is {self.client_object}')

        except Exception as e:
            # Send message to client via JSON and close the connection
            self.send(text_data=json.dumps({
                'error': 'Player does not exist'
            }))
            self.close()

    # Initialize the game and makes sure that both players are connected before starting the game
    async def initialize_game(self):
        try:
            # Create the game
            ic(f'Creating game for match {self.match_id}')
            game = Game(
                dictKeyboard=self.keyboard_inputs,  # This is a dictionary that holds the keyboard inputs for each match (eg. self.keyboard_inputs = {"up.1": False, "down.1": False, "up.2": False, "down.2": False})
                leftPlayer=self.left_player,        # This is the Player object for the left player for the game
                rightPlayer=self.right_player,      # This is the Player object for the right player for the game
                scoreLimit=self.scorelimit,         # This is the score limit for the game
            )

            ic(f'Trying to add game to index {self.match_id}')
            # If the game was successfully created, add it to the list of games
            self.list_of_games[self.match_id] = game

            ic(f'Successfully added game to index {self.match_id}')
        except Exception as e:
            ic(f'Error during game initialization: {e}')

        try:
            # In case the game is created and both players are connected, start the game
            ic(f'Starting game {self.match_id}')
            if self.list_of_games[self.match_id] and not self.list_of_games[self.match_id].isAlive():
                # Check if both players for this match are connected
                if self.client_id in self.list_of_players and self.player_1_id in self.list_of_players and self.player_2_id in self.list_of_players:
                    ic(f'Sending start command to game {self.match_id}')
                    self.list_of_games[self.match_id].start()
                    asyncio.create_task(self.game_update())
                else:
                    ic(f'Cannot start game. Both players for this match are not connected yet.')
        except Exception as e:
            ic(f'Error during game start: {e}')

    # Handles the initial connection
    async def connect(self):
        try:
            query_string = self.scope['query_string'].decode('utf-8')
            query_params = parse_qs(query_string)
            self.match_id = self.scope['url_route']['kwargs']['match_id']
            self.player_1_id = query_params.get('player_1_id', [None])[0]
            self.player_2_id = query_params.get('player_2_id', [None])[0]
            self.client_id = query_params.get('client_id', [None])[0]
            self.scorelimit = query_params.get('scorelimit', [None])[0]

            ic(f'Connecting to match {self.match_id} with client {self.client_id}. Player 1: {self.player_1_id}. Player 2: {self.player_2_id}')

            await self.get_match(self.match_id)
            await self.get_user(self.client_id)

            ic(f'Connected to match {self.match_id} with client {self.client_id}. Player 1: {self.player_1_id}. Player 2: {self.player_2_id}')

            # Check if the client is already connected as a player or obeserver in another match
            if self.client_id in self.list_of_players or self.client_id in self.list_of_observers:
                # Send message to client via JSON and close the connection
                await self.send(text_data=json.dumps({
                    'error': 'Client is already connected to another match'
                }))
                await self.close()

            await self.accept()

            # Check if client is a player or observer
            if self.client_id == self.player_1_id or self.client_id == self.player_2_id:
                self.list_of_players[self.client_id] = self.channel_name

            else:
                ic(f'Client {self.client_id} is an observer')
                self.list_of_observers[self.client_id] = self.channel_name

            ic(f'Accepted connection to match {self.match_id} with client {self.client_id}. Player 1: {self.player_1_id}. Player 2: {self.player_2_id}')

            if self.client_id == self.player_1_id or self.client_id == self.player_2_id:
                # Initialize the keyboard inputs for this match with the player ids so each client has its own digital keyboard
                self.keyboard[self.player_1_id] = {"up": f"up.{self.player_1_id}", "down": f"down.{self.player_1_id}", "left": "xx", "right": "xx"}
                self.keyboard[self.player_2_id] = {"up": f"up.{self.player_2_id}", "down": f"down.{self.player_2_id}", "left": "xx", "right": "xx"}

                # Initialize the Player objects for the left and right players. This is not the client model but instead the Player object from the game
                self.left_player = Player(name=self.player_1_id, binds=self.keyboard[self.player_1_id])
                self.right_player = Player(name=self.player_2_id, binds=self.keyboard[self.player_2_id])

                self.keyboard_inputs = {
                    f'up.{self.player_1_id}' : False,
                    f'down.{self.player_1_id}' : False,
                    f'up.{self.player_2_id}' : False,
                    f'down.{self.player_2_id}' : False,
                }

                self.list_of_keyboard_inputs[self.match_id] = self.keyboard_inputs

                self.list_of_games[self.match_id] = None
                
            # Add client to the channel group for this match, this allows us to send messages to all clients in the group
            await self.channel_layer.group_add(
                self.match_id,
                self.channel_name
            )

            # Send message to group announcing new player
            await self.broadcast_to_group(self.match_id, 'player_list', self.list_of_players)

        except Exception as e:
            ic(f'Error during connection: {e}')
            # Send message to client via JSON and close the connection if there is an error
            await self.close()


    # Messaging helper function
    async def broadcast_to_group(self, group_name, command, data):
        print(f'Channel Broadcasting {command} to group {group_name}')

        # Send message to group, this utilizes channel_layer.group_send
        # channel_layer.group_send: This is a low-level function to send a message directly to a group of channels.
        # The type key in the message is used to route the message to a consumer. In this case, the consumer is the broadcast function.
        await self.channel_layer.group_send(
            group_name,
            {
                'type': 'broadcast',
                'command': command,
                'data': data
            })

    async def broadcast(self, event):
        # The event holds the data that was sent in the group_send function, this function is called by the channel layer and is not called directly.
        # Its called for each member of the group sending the command and data found in the event
        command = event['command']
        data = event['data']
        print(f'Sending message to client {self.client_id} with data: {data}')
        await self.send(text_data=json.dumps({
            'type': command,
            'data': data
        }))

    # Disconnect
    async def disconnect(self, close_code):
        try:
            match_object = self.get_match(self.match_id)
            match_object.active = False
            # match_object.player1_score = self.player_1_score
            # match_object.player2_score = self.player_2_score
            match_object.save()
            # await self.get_match(self.match_id)
            ic(f'Disconnecting from match {self.match_id} with client {self.client_id}. Player 1: {self.player_1_id}. Player 2: {self.player_2_id}')
            if self.client_id in self.list_of_players:
                ic(f'Stopping game {self.match_id}')
                if self.list_of_games.get(self.match_id) and self.list_of_games[self.match_id].isAlive():
                    ic(f'Sending stop command to game {self.match_id}')
                    self.list_of_games[self.match_id].stop()

                # Remove the player from the list of players
                del self.list_of_players[self.client_id]
                del self.list_of_games[self.match_id]
                del self.list_of_keyboard_inputs[self.match_id]


        except Exception as e:
            ic(f'Error during disconnect: {e}')

        if self.client_id in self.list_of_observers:
            # Remove the observer from the list of observers if it is in the list
            del self.list_of_observers[self.client_id]

        # Remove the client from the channel group for this match
        await self.channel_layer.group_discard(
            self.match_id,
            self.channel_name
        )

        # Send message to group announcing player left
        await self.broadcast_to_group(self.match_id, 'player_list', self.list_of_players)
        await self.close(code=close_code)

    # Receive message from WebSocket and process it
    async def receive(self, text_data):
        # Whenever a client sends a message to the server, the server will process the message and send a response back to the client. We recieve text_data in the
        # form of a JSON string. We parse the JSON string into a dictionary and extract the command and data from the dictionary.
        data = json.loads(text_data)
        command = data.get('command')
        key_status = data.get('key_status')
        
        ic(f'Received command: {command} with data: {data}')

        if command == 'player_list':
            await self.send(text_data=json.dumps({
                'type': 'player_list',
                'data': list(self.list_of_players.keys()),
            }))
              
        elif command == 'start_game':
            ic(f'Sending start command to game {self.match_id}')
            if not self.list_of_games.get(self.match_id):
                ic(f'Initializing game {self.match_id}')
                await self.initialize_game()
            if self.list_of_games[self.match_id] and not self.list_of_games[self.match_id].isAlive():
                # Check if both players for this match are connected
                if self.client_id in self.list_of_players and self.player_1_id in self.list_of_players and self.player_2_id in self.list_of_players:

                    self.list_of_games[self.match_id].start()
                    asyncio.create_task(self.game_update())
                else:
                    ic(f'Cannot start game. Both players for this match are not connected yet.')

        elif command == 'keyboard':
            ic(f'Updating keyboard for client {self.client_id} with data: {data}')
            if self.list_of_games[self.match_id]:
                if self.list_of_games[self.match_id] and self.list_of_games[self.match_id].isAlive() and self.left_player and self.right_player:
                    if key_status == 'on_press':
                        key = data.get('key')
                        self.on_press(key)
                    elif key_status == 'on_release':
                        key = data.get('key')
                        self.on_release(key)

        elif command == 'disconnect':
            ic(f'Disconnecting client {self.client_id}')
            await self.disconnect(1000)


    # Game update loop for sending game state to the group
    async def game_update(self):
        ic(f'Starting the game update loop for match {self.match_id}')
        try:
            target_fps = 60
            update_interval = 1 / target_fps

            while self.match_id in self.list_of_games and self.list_of_games[self.match_id] and self.list_of_games[self.match_id].isAlive():
                # Update paddle positions based on keyboard inputs
                left_paddle = self.list_of_games[self.match_id]._leftPaddle
                right_paddle = self.list_of_games[self.match_id]._rightPaddle

                self.player_1_score = self.list_of_games[self.match_id]._leftPlayer.getScore()
                self.player_2_score = self.list_of_games[self.match_id]._rightPlayer.getScore()

                left_paddle.updatePosition()
                right_paddle.updatePosition()

                # Send updated game state to the group
                await self.broadcast_to_group(self.match_id, 'game_update', self.list_of_games[self.match_id].reportScreen())
                await self.broadcast_to_group(self.match_id, 'score_update', {'left': self.list_of_games[self.match_id]._leftPlayer.getScore(), 'right': self.list_of_games[self.match_id]._rightPlayer.getScore()})

                try:
                    # await asyncio.sleep(update_interval) # For use with FPS
                    await asyncio.sleep(0) # For manual control of FPS

                except asyncio.CancelledError:
                    ic(f'Game update for match {self.match_id} cancelled')
                    break
                except Exception as e:
                    ic(f'Error during game update for match {self.match_id}: {e}')

        except KeyError:
            ic(f'Match {self.match_id} not found in list_of_games. Stopping game update.')
        finally:
            self.list_of_games[self.match_id] = None
            ic(f'Game update for match {self.match_id} stopped')

        await self.disconnect(1000)



    # Keyboard input processing and formatting
    def on_press(self, key):
        ic(f'I am player {self.client_id}, my keyboard is {self.keyboard.get(str(self.client_id), {})} and the key is {key}')

        # Format the key to match the format used in the game. Example: up.1 for client 1 pressing the up key
        formatted_key = f'{key}.{self.client_id}'
        ic(f'Trying to update key {formatted_key} for match {self.match_id}')
        
        asyncio.get_event_loop().call_soon_threadsafe(self.update_key, formatted_key, True)

    def on_release(self, key):
        ic(f'I am player {self.client_id}, my keyboard is {self.keyboard.get(str(self.client_id), {})} and the key is {key}')

        # Format the key to match the format used in the game. Example: up.342 for client 342 releasing the up key
        formatted_key = f'{key}.{self.client_id}'
        ic(f'Trying to update key {formatted_key} for match {self.match_id}')
        
        asyncio.get_event_loop().call_soon_threadsafe(self.update_key, formatted_key, False)

    # Does the actual updating of the keyboard input for the game
    def update_key(self, formatted_key, is_pressed):
        # Checks if the match_id has a keyboard input list and if the formatted key is in that list 
        if self.match_id in self.list_of_keyboard_inputs and formatted_key in self.list_of_keyboard_inputs[self.match_id]:
            # If the keyboard for the match_id has the formatted key, update the value of the key to the new value (True or False)
            self.list_of_keyboard_inputs[self.match_id][formatted_key] = is_pressed
            ic(f'Successfully updated key {formatted_key} for match {self.match_id}')
        else:
            ic(f'Invalid match_id {self.match_id} or key {formatted_key}')
