import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from ws_api.python_pong.Player import Player
from ws_api.python_pong.Game import Game
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.utils import timezone
from django.db import transaction
from api.jwt_utils import get_user_id_from_jwt_token

# Commands:
# The consumer handles formatting they keys. Client only needs to send the key and key_status.
# Use start/top ball to start and pause the game.
# Finalize match is used to finalize the match and update the database Match Object.

# {"command": "keyboard", "key_status": "on_press", "key": "up"}
# {"command": "keyboard", "key_status": "on_release", "key": "down"}
# {"command": "start_ball"}
# {"command": "stop_ball"}
# {"command": "save_models"}

def set_frame_rate(fps):
    if fps < 1 or fps > 60 or type(fps) != int:
        fps = 60
    frame_dur = 1/fps
    return frame_dur

class PongConsumer(AsyncWebsocketConsumer):
    list_of_players = {}        # Hold the user instances of the players in the match
    user_by_match = {}          # Holds the users in the match by match ID
    shared_game_keyboard = {}   # Holds the the shared game keyboard to manipulate the game.
    shared_game_task = {}       # Holds the task for the shared game, in order to cancel it when the game is stopped.
    shared_game = {}            # Holds the shared game object for the match.
    run_game = {}               # Boolean to run/pause the game.
    finished = {}               # Boolean to determine if the game is finished or not
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_object = None   # Holds the model object of the client
        self.keyboard = {}          # Holds the keyboard inputs for each player (eg. self.keyboard[self.player_1_id] = {"up": f"up.{self.player_1_id}", "down": f"down.{self.player_1_id}", "left": "xx", "right": "xx"})
        self.list_of_players = {}   # Holds the Player objects for each player in the match (eg. self.list_of_players[self.player_1_id] = Player(self.player_1_id, self.player_1_name, self.player_1_avatar, self.player_1_ELO))
        self.left_player = None     # Holds the Player object for the left player for the game
        self.right_player = None    # Holds the Player object for the right player for the game
        self.player_1_id = None     # Holds the ID of the left player for the game
        self.player_2_id = None     # Holds the ID of the right player for the game
        self.player_1_score = 0     # Holds the score of the left player for the game
        self.player_2_score = 0     # Holds the score of the right player for the game
        self.match_object = None    # Holds the Match object for the game
        self.match_id = None        # Holds the ID of the match
        self.client_id = None       # Holds the ID of the client

# Async Database Methods
    @database_sync_to_async
    def load_models(self, match_id):
        try:
            from api.tournament.models import Match
            from api.userauth.models import CustomUser as User
            PongConsumer.run_game[self.match_id] = False
            
            print(f'Getting Match: {match_id}, game_run_state: {PongConsumer.run_game[self.match_id]}')
            
            self.match_object = Match.objects.get(id=match_id)
            print(f'Match Object Found: {self.match_object}')

            self.player_object = User.objects.get(id=self.client_id)
            print(f'Player Object Found: {self.player_object}')
            
            self.player_1_id = str(self.match_object.player1.id)
            self.player_2_id = str(self.match_object.player2.id)
            self.scorelimit = 7
            print(f'Player 1 ID: {self.player_1_id}, Player 2 ID: {self.player_2_id}, score_limit: {self.scorelimit}')

            if not PongConsumer.list_of_players.get(self.match_id):
                PongConsumer.list_of_players[self.match_id] = dict()
            PongConsumer.list_of_players[self.match_id][self.client_id] = self
            print(f'List of Players in all PongConsumer Instances: {PongConsumer.list_of_players}')
            self.list_of_players[self.player_1_id] = User.objects.get(id=self.player_1_id)
            self.list_of_players[self.player_2_id] = User.objects.get(id=self.player_2_id)
            print(f'List of Players in this PongConsumer Instance: {self.list_of_players}')
            
            self.keyboard[self.player_1_id] = {"up": f"up.{self.player_1_id}", "down": f"down.{self.player_1_id}", "left": "xx", "right": "xx"}
            self.keyboard[self.player_2_id] = {"up": f"up.{self.player_2_id}", "down": f"down.{self.player_2_id}", "left": "xx", "right": "xx"}
            print(f'Keyboard: {self.keyboard[self.player_1_id]}, {self.keyboard[self.player_2_id]}')
            
            self.left_player = Player(name=self.player_1_id, binds=self.keyboard[self.player_1_id])
            self.right_player = Player(name=self.player_2_id, binds=self.keyboard[self.player_2_id])
            print(f'Left Player Object: {self.left_player}, Right Player Object: {self.right_player}')
            
            PongConsumer.shared_game_keyboard[self.match_id] = {
                f'up.{self.player_1_id}': False,
                f'down.{self.player_1_id}': False,
                f'up.{self.player_2_id}': False,
                f'down.{self.player_2_id}': False,
            }
            print(f'Keyboard Inputs for Match {self.match_id}: {self.shared_game_keyboard[self.match_id]}')
            
            PongConsumer.shared_game[self.match_id] = Game(
                dictKeyboard=PongConsumer.shared_game_keyboard[self.match_id],
                leftPlayer=self.left_player,        # This is the Player object for the left player for the game
                rightPlayer=self.right_player,      # This is the Player object for the right player for the game
                scoreLimit=self.scorelimit,    
            )
            print(f'Shared Game Object for Match {self.match_id}: {PongConsumer.shared_game[self.match_id]}')
                
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
    @transaction.atomic
    def save_models(self, disconnect=False, close_code=1000):
        from api.tournament.models import Match
        from api.userauth.models import CustomUser as User

        if PongConsumer.finished.get(self.match_id) == True:
            return

        try:
            match_object = Match.objects.select_for_update().get(id=self.match_id)
            match_object.player1_score = PongConsumer.shared_game[self.match_id]._leftPlayer.getScore()
            match_object.player2_score = PongConsumer.shared_game[self.match_id]._rightPlayer.getScore()

            player1_id = self.player_1_id
            player2_id = self.player_2_id

            print(f"Player 1 Score: {match_object.player1_score}, Player 2 Score: {match_object.player2_score}")
            print(f"DISCONNECTED: {self.client_id}, bool: {disconnect}")
            print(f'Match finished, scores: {match_object.player1_score}')
            if disconnect:
                # winner = self.player_1_id if int(self.client_id) == self.player_2_id else self.player_2_id
                 
                if int(self.client_id) == int(self.player_1_id):
                    winner = int(self.player_2_id)
                else:
                    winner = int(self.player_1_id)
                match_object.winner = User.objects.get(id=winner)
            elif match_object.player1_score == match_object.player2_score:
                # Handle tie by comparing ELO scores
                player1_elo = User.objects.get(id=player1_id).ELO
                player2_elo = User.objects.get(id=player2_id).ELO

                print(f"Player 1 ELO: {player1_elo}, Player 2 ELO: {player2_elo}")

                if player1_elo > player2_elo:
                    match_object.winner = User.objects.get(id=player1_id)
                elif player1_elo < player2_elo:
                    match_object.winner = User.objects.get(id=player2_id)
                else:
                    # If ELO scores are also the same, you can handle it as needed
                    match_object.winner = None  # For example, set winner to None in case of a tie

                if match_object.winner:
                    print(f"Tiebreaker - Winner: {match_object.winner}, Loser: {match_object.loser()}")
                else:
                    print(f"Tiebreaker - It's a tie!")

            else:
                # Determine the winner based on the score
                print("here")
                # match_object.winner = User.objects.get(id=player1_id) if match_object.player1_score > match_object.player2_score else User.objects.get(id=player2_id)
                if match_object.player1_score > match_object.player2_score:
                    match_object.winner = User.objects.get(id=int(player1_id))
                else:
                    match_object.winner = User.objects.get(id=int(player2_id))
                print(f"Winner: {match_object.winner}, Loser ID: {match_object.loser()}")

            match_object.date_played = timezone.now()
            match_object.active = False
            match_object.save()

            PongConsumer.finished[self.match_id] = True

            print(f'WINNER: {match_object.winner}')

            if match_object.winner:
                winner_id = match_object.winner.id
                loser_id = match_object.loser().id

                # Update ELO scores
                winner_object = User.objects.get(id=winner_id)
                loser_object = User.objects.get(id=loser_id)

                # Split the ELO change equally among the tied players
                elo_change = 15  # Adjust the value as needed
                elo_change_per_player = elo_change / 2

                winner_object.ELO = max(0, winner_object.ELO + elo_change_per_player)
                loser_object.ELO = max(0, loser_object.ELO - elo_change_per_player)

                winner_object.save()
                loser_object.save()
                
                print(f"Match finalized. Winner ID: {winner_id}, Loser ID: {loser_id}, Winner ELO: {winner_object.ELO}, Loser ELO: {loser_object.ELO}")
                match_object.save()
                # Send the match results back to the client
                return {
                    "winner_id": winner_id,
                    # "winner_avatar": match_object.winner.avatar.url,
                    "winner_username": match_object.winner.username if match_object.winner else None,
                    "player1_id": match_object.player1.id,
                    "player1_username": match_object.player1.username,
                    "player2_id": match_object.player2.id,
                    "player2_username": match_object.player2.username,
                    "loser_id": loser_id,
                    "player1_score": match_object.player1_score,
                    "player2_score": match_object.player2_score,
                    "winner_elo": winner_object.ELO,
                    "loser_elo": loser_object.ELO,
                }
                
        except Match.DoesNotExist as e:
            print(f"Match with ID {self.match_id} does not exist.")
        except User.DoesNotExist as e:
            print(f"User not found. Winner ID: {winner_id}, Loser ID: {loser_id}")
        except Exception as e:
            print(f"An error occurred during match finalization: {e}")

# -----------------------------
  
# Websocket Methods
    async def check_reconnect(self):
        seconds_to_wait = 6
        for seconds in range(seconds_to_wait):
            print("Waiting for reconnect...")
            await self.broadcast_to_group(f"{self.match_id}", "message", {
                "message": "Waiting for opponent to reconnect",
                "seconds_left": f"{seconds_to_wait - seconds - 1} seconds"
            })
            await asyncio.sleep(1)
            if len(PongConsumer.list_of_players[self.match_id].keys()) == 2:
                PongConsumer.run_game[self.match_id] = True
                PongConsumer.shared_game_task = asyncio.create_task(self.start_game(None))
                return
        return

    async def disconnect(self, close_code=1000):
        # await self.broadcast_to_group(f"{self.match_id}", "message", {
        #     "message": "User Disconnected",
        #     "client_id": self.client_id,
        # })

        if self.client_id in PongConsumer.list_of_players[self.match_id]:
            del PongConsumer.list_of_players[self.match_id][self.client_id]

        PongConsumer.run_game[self.match_id] = False
        try:
            res = await self.save_models(disconnect=True)
            if res:
                await self.broadcast_to_group(str(self.match_id), "match_finished", res)
        except:
            pass
        await self.discard_channels()

        await self.close()
        
    async def connect(self):
        try:
            query_string = self.scope['query_string'].decode('utf-8')
            query_params = parse_qs(query_string)
            self.match_id = self.scope['url_route']['kwargs']['match_id']

            if not query_params.get('token'):
                await self.close()
            print(f'JWT Token: {query_params.get("token")}')
            token = query_params['token'][0]

            try:
                user_id = get_user_id_from_jwt_token(token)
                self.client_id = str(user_id)
                print(f'Client ID: {self.client_id}')
                await self.channel_layer.group_add(f"{self.match_id}.client_id", self.channel_name)
                await self.channel_layer.group_add(f"{self.match_id}", self.channel_name)
                await self.load_models(self.match_id)
            except Exception as e:
                await self.close()
                print(e)

            if self.client_id not in (self.player_1_id, self.player_2_id):
                print(f'Client ID: {self.client_id}: Not a player in this match')
                await self.close()
                
            await self.accept()

            PongConsumer.finished[self.match_id] = False

            if not self.match_object.active:
                await self.send(text_data=json.dumps({
                    "type": "inactive_match",
                    "message": "The match you are trying to join already finished"
                }))
                await self.close()
                        
            print(f'List of Players: {PongConsumer.list_of_players}')
            
            await self.broadcast_to_group(f"{self.match_id}", "message", {
                "message": "User Connected",
                "client_id": self.client_id,
                "connected_users": list(PongConsumer.list_of_players[self.match_id].keys()),
                })
            
            if self.player_1_id in PongConsumer.list_of_players[self.match_id] and self.player_2_id in PongConsumer.list_of_players[self.match_id]:
                await self.broadcast_to_group(f"{self.match_id}", "message", {
                    "message": 'Game Ready',
                })
            else:
                await self.broadcast_to_group(f"{self.match_id}", "message", {
                    "message": 'Please refresh the page',
                })
                  
        except Exception as e:
            print(e)
            await self.close()
# -----------------------------

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
            data = json.loads(text_data)
            print(f'Received data: {data}')

            if not data.get('command'):
                return

            if data['command'] == 'keyboard' and PongConsumer.run_game[self.match_id]:
                await self.keyboard_input(data)
            elif data['command'] == 'start_ball':
                PongConsumer.run_game[self.match_id] = True
                PongConsumer.shared_game_task[self.match_id] = asyncio.create_task(self.start_game(data))

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
                # print(f'Key Pressed: {formatted_key}')
                PongConsumer.shared_game_keyboard[self.match_id][formatted_key] = True
                # print(f'Game Keyboard Status: {PongConsumer.shared_game_keyboard[self.match_id]}')
            elif key_status == 'on_release':
                # print(f'Key Released: {formatted_key}')
                PongConsumer.shared_game_keyboard[self.match_id][formatted_key] = False
                # print(f'Game Keyboard Status: {PongConsumer.shared_game_keyboard[self.match_id]}')
            else:
                print(f'Unknown key status: {key_status}, {formatted_key}')
                    
        except Exception as e:
            print(e)
            await self.close()
            
    async def start_game(self, data):
        try:
            while PongConsumer.run_game[self.match_id] is True:
                PongConsumer.shared_game[self.match_id].pointLoop2()

                left_score = PongConsumer.shared_game[self.match_id]._leftPlayer.getScore()
                right_score = PongConsumer.shared_game[self.match_id]._rightPlayer.getScore()

                if left_score >= self.scorelimit or right_score >= self.scorelimit:
                    PongConsumer.run_game[self.match_id] = False
                    await self.broadcast_to_group(str(self.match_id), "match_finished", await self.save_models())
                    PongConsumer.finished[self.match_id] = True
                    await asyncio.sleep(0.5)
                    await self.close()
                    return

                await self.broadcast_to_group(f"{self.match_id}", "screen_report", {
                    "game_update": PongConsumer.shared_game[self.match_id].reportScreen(),
                    "left_score": left_score,
                    "right_score": right_score
                })
                await asyncio.sleep(set_frame_rate(60))

            await asyncio.sleep(0.5)
            if PongConsumer.finished[self.match_id] == True:
                await self.close()
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
                f"{self.match_id}.player_1_id",
                self.channel_name
            )
            await self.channel_layer.group_discard(
                f"{self.match_id}.player_2_id",
                self.channel_name
            )
            
        except Exception as e:
            print(e)
            await self.close()
    

        