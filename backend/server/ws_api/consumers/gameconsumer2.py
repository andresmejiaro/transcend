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
from api.jwt_utils import get_user_id_from_jwt_token


def set_frame_rate(fps):
    if fps < 1 or fps > 60 or type(fps) != int:
        fps = 60
    frame_dur = 1/fps
    return frame_dur

class PongConsumer(AsyncWebsocketConsumer):
    list_of_players = {}
    shared_game_keyboard = {}
    shared_game_task = {}
    shared_game = {}
    run_game = {}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_object = None   # Holds the model object of the client
        self.keyboard = {}          # Holds the keyboard inputs for each player (eg. self.keyboard[self.player_1_id] = {"up": f"up.{self.player_1_id}", "down": f"down.{self.player_1_id}", "left": "xx", "right": "xx"})
        self.list_of_players = {}   # Holds the Player objects for each player in the match (eg. self.list_of_players[self.player_1_id] = Player(self.player_1_id, self.player_1_name, self.player_1_avatar, self.player_1_ELO))
        self.left_player = None     # Holds the Player object for the left player for the game
        self.right_player = None    # Holds the Player object for the right player for the game
        self.player_1_id = None     # Holds the ID of the left player for the game
        self.player_2_id = None     # Holds the ID of the right player for the game
        self.player_1_score = 0
        self.player_2_score = 0
        self.update_buffer = []
        self.match_object = None
        self.user_object = None
        self.match_id = None
        self.client_id = None
        PongConsumer.run_game[self.match_id] = False

    @database_sync_to_async
    def get_match(self, match_id):
        try:
            from api.tournament.models import Match
            from api.userauth.models import CustomUser as User

            print(f'Match ID: {match_id}')
            self.match_object = Match.objects.get(id=match_id)
            print(f'Match Object: {self.match_object}')
            self.player_object = User.objects.get(id=self.client_id)
            print(f'Player Object: {self.player_object}')
            
            self.player_1_id = str(self.match_object.player1.id)
            self.player_2_id = str(self.match_object.player2.id)
            self.scorelimit = 7
            
            print(f'Player 1 ID: {self.player_1_id}, Player 2 ID: {self.player_2_id}, score_limit: {self.scorelimit}')
                
            PongConsumer.list_of_players[self.client_id] = self
            
            print(f'List of Players: {PongConsumer.list_of_players}')
            
            if self.client_id == self.player_1_id or self.client_id == self.player_2_id:
                self.keyboard[self.player_1_id] = {"up": f"up.{self.player_1_id}", "down": f"down.{self.player_1_id}", "left": "xx", "right": "xx"}
                self.keyboard[self.player_2_id] = {"up": f"up.{self.player_2_id}", "down": f"down.{self.player_2_id}", "left": "xx", "right": "xx"}

            print(f'Keyboard: {self.keyboard[self.player_1_id]}, {self.keyboard[self.player_2_id]}')
            
            self.left_player = Player(name=self.player_1_id, binds=self.keyboard[self.player_1_id])
            self.right_player = Player(name=self.player_2_id, binds=self.keyboard[self.player_2_id])
            
            print(f'Left Player: {self.left_player}, Right Player: {self.right_player}')
            
            PongConsumer.shared_game_keyboard[self.match_id] = {
                f'up.{self.player_1_id}': False,
                f'down.{self.player_1_id}': False,
                f'up.{self.player_2_id}': False,
                f'down.{self.player_2_id}': False,
            }
            print(f'Keyboard Inputs: {self.shared_game_keyboard[self.match_id]}')
            
            PongConsumer.shared_game[self.match_id] = Game(
                dictKeyboard=PongConsumer.shared_game_keyboard[self.match_id],
                leftPlayer=self.left_player,        # This is the Player object for the left player for the game
                rightPlayer=self.right_player,      # This is the Player object for the right player for the game
                scoreLimit=self.scorelimit,    
            )
            
            print(f'Game: {PongConsumer.shared_game[self.match_id]}')
                          
        except Match.DoesNotExist:
            print(f"Match with ID {match_id} does not exist.")
            self.close()
        except User.DoesNotExist:
            print(f"User with ID {self.client_id} does not exist.")
            self.close()
        except Exception as e:
            print(e)
            self.close()
    
    @database_sync_to_async
    def finalize_match(self, data):
        from api.tournament.models import Match
        from api.userauth.models import CustomUser as User
        
        match_object = Match.objects.get(id=self.match_id)
        match_object.player1_score = self.left_player.getScore()
        match_object.player2_score = self.right_player.getScore()
        if match_object.player1_score > match_object.player2_score:
            winner = self.player_1_id
        else:
            winner = self.player_2_id
        match_object.winner = User.objects.get(id=winner)
        match_object.date_played = timezone.now()
        match_object.active = False
        match_object.save()
    
    async def disconnect(self, close_code):
        await self.discard_channels()
        if self.client_id in PongConsumer.list_of_players:
            del PongConsumer.list_of_players[self.client_id]
        if self.client_id == self.player_1_id or self.client_id == self.player_2_id:
            PongConsumer.run_game = False
            await self.broadcast_to_group(f"{self.match_id}", "message", {
                "message": "Game Stopped",
            })
        await self.broadcast_to_group(f"{self.match_id}", "message", {
            "message": "User Disconnected",
            "client_id": self.client_id,
        })
            
        await self.close()
        
    async def connect(self):
        try:
            query_string = self.scope['query_string'].decode('utf-8')
            query_params = parse_qs(query_string)
            self.match_id = self.scope['url_route']['kwargs']['match_id']
            
            print(f'Match ID: {self.match_id}')

            if not query_params.get('token'):
                await self.close()
            print(f'Token: {query_params.get("token")}')
            token = query_params['token'][0]

            try:
                user_id = get_user_id_from_jwt_token(token)
                self.client_id = str(user_id)
                print(f'Client ID: {self.client_id}')
                await self.channel_layer.group_add(f"{self.match_id}.client_id", self.channel_name)
                await self.channel_layer.group_add(f"{self.match_id}", self.channel_name)
                await self.get_match(self.match_id)
            except Exception as e:
                await self.close()
                print(e)
                
            await self.accept()
                        
            print(f'List of Players: {PongConsumer.list_of_players}')
            
            await self.broadcast_to_group(f"{self.match_id}", "message", {
                "message": "User Connected",
                "client_id": self.client_id,
                "connected_users": list(PongConsumer.list_of_players.keys()),
                })
            
            if self.player_1_id in PongConsumer.list_of_players and self.player_2_id in PongConsumer.list_of_players:
                await self.broadcast_to_group(f"{self.match_id}", "message", {
                    "message": 'Game Ready',
                })
                  
        except Exception as e:
            print(e)
            await self.close()

# Messaging Handling Methods
    async def broadcast_to_group(self, group_name, command, data):
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
        #print(f'Sending message to client {self.client_id} with data: {data}')
        await self.send(text_data=json.dumps({
            'type': command,
            'data': data
        }))             
               
    async def receive(self, text_data):
        try:
            asyncio.sleep(0.1)
            data = json.loads(text_data)
            print(f'Received data: {data}')
            if data['command'] == 'keyboard':      # Send the keyboard input to the other player and to the game
                await self.keyboard_input(data)
            elif data['command'] == 'start_ball':
                PongConsumer.run_game[self.match_id] = True
                PongConsumer.shared_game_task[self.match_id] = asyncio.create_task(self.start_game(data))
            elif data['command'] == 'stop_ball':
                PongConsumer.run_game[self.match_id] = False
            elif data['command'] == 'finalize_match':
                await self.finalize_match(data)

        except Exception as e:
            print(e)
            await self.close()
# -----------------------------

# Game Methods       
    async def keyboard_input(self, data):
        try:
            key_status = data.get('key_status')
            key = data.get('key')
            formatted_key = f'{key}.{self.client_id}'
            print(f'Key Status: {key_status}')
            
            await asyncio.sleep(0.01)

            if key_status == 'on_press':
                print(f'Key Pressed: {formatted_key}')
                PongConsumer.shared_game_keyboard[self.match_id][formatted_key] = True
                print(f'Game Keyboard Status: {PongConsumer.shared_game_keyboard[self.match_id]}')
            elif key_status == 'on_release':
                print(f'Key Released: {formatted_key}')
                PongConsumer.shared_game_keyboard[self.match_id][formatted_key] = False
                print(f'Game Keyboard Status: {PongConsumer.shared_game_keyboard[self.match_id]}')
            else:
                print(f'Unknown key status: {key_status}, {formatted_key}')
                    
        except Exception as e:
            print(e)
            await self.close()
            
    async def start_game(self, data):
        try:
            while PongConsumer.run_game[self.match_id] is True:
                PongConsumer.shared_game[self.match_id].pointLoop2()
                await self.broadcast_to_group(f"{self.match_id}", "screen_report", {
                    "game_update": PongConsumer.shared_game[self.match_id].reportScreen(),
                    "left_score": PongConsumer.shared_game[self.match_id]._leftPlayer.getScore(),
                    "right_score": PongConsumer.shared_game[self.match_id]._rightPlayer.getScore(),
                })
                await asyncio.sleep(set_frame_rate(30))
        except asyncio.CancelledError:
            print('Game stopped')
        except Exception as e:
            print(e)
            await self.close()   
# -----------------------------

# Channel Methods
    async def discard_channels(self):
        try:
            print(f'Channel Disconnected')
            await self.channel_layer.group_discard(
                f"{self.match_id}",
                self.channel_name
            )
            await self.channel_layer.group_discard(
                f"{self.match_id}.client_id",
                self.channel_name
            )

            if self.client_id in PongConsumer.list_of_players:
                del PongConsumer.list_of_players[self.client_id]
            
        except Exception as e:
            print(e)
            await self.close()
    
            
