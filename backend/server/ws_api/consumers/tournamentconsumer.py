import json
from channels.generic.websocket import AsyncWebsocketConsumer
from ws_api.python_pong.Player import Player
from ws_api.python_pong.Game import Game
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
import math
import random
import logging

from django.utils.module_loading import import_string



class TournamentConsumer(AsyncWebsocketConsumer):

    list_of_player_channels = {}
    list_of_player_objects = {}
    list_of_matches = {}
    list_of_rounds = {}
    tournament_admin_id = None
    tournament_object = None
    tournament_rounds_to_complete = 0
    current_round = 0
    tournament_id = None
    tournament_ended = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = None
        self.player_object = None
        self.player_score = 0

# Define constants for commands

    START_TOURNAMENT = 'start_tournament'
    END_MATCH = 'end_match'
    START_ROUND = 'start_round'
    END_ROUND = 'end_round'
    ADD_PLAYER = 'add_player'
    REMOVE_PLAYER = 'remove_player'
    LIST_PLAYERS = 'list_players'
    LIST_MATCHES = 'list_matches'
    LIST_ROUNDS = 'list_rounds'
    CMD_NOT_FOUND = 'command_not_found'


# Channel methods (Connect, Disconnect, Receive)
    async def connect(self):
        query_string = self.scope['query_string'].decode('utf-8')
        query_params = parse_qs(query_string)
        self.tournament_id = self.scope['url_route']['kwargs']['tournament_id']
        self.client_id = query_params['client_id'][0]

        # Get the user and see if they exist before accepting the connection
        self.player_object = await self.init_player_obj(self.client_id)
        if self.player_object is None:
            await self.close()
            return

        await self.accept()

        # Add client to the group channel
        print(f'Adding {self.client_id} to group {self.tournament_id}')
        await self.channel_layer.group_add(
            self.tournament_id,
            self.channel_name
        )
        await self.channel_layer.group_add(
            self.client_id,
            self.channel_name
        )

        # if not self.list_of_player_channels:
        #     self.start_tournament()

        await self.broadcast_to_group(
            self.tournament_id,
            'new_player',
            {
                'player_id': self.client_id,
                'tournament_id': self.tournament_id,
                'players': self.list_of_player_channels,
            }
        )

    async def disconnect(self, close_code):
        try:
            print(f'Client {self.client_id} disconnected with code {close_code}')
            # Remove client from the group channel
            await self.channel_layer.group_discard(
                str(self.tournament_id),
                self.channel_name
            )
            await self.channel_layer.group_discard(
                str(self.client_id),
                self.channel_name
            )
            # Remove client from the list of players or observers
            if self.client_id in self.list_of_player_channels:
                del self.list_of_player_channels[self.client_id]

            # Send info of group status every time a client leaves
            await self.broadcast_to_group(
                str(self.tournament_id),
                'player_left',
                {
                    'player_id': self.client_id,
                }
            )

            # If the tournament admin leaves, end the tournament and kick everyone out save current state
            if self.client_id == self.tournament_admin_id:
                await self.broadcast_to_group(
                    str(self.tournament_id),
                    'tournament_ended',
                    {
                        'tournament_id': self.tournament_id,
                        'info': 'Tournament admin left the tournament. The tournament has ended.',
                    }
                )
                self.tournament_ended = True

        except Exception as e:
            print(f"Error in disconnect method: {e}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            command = data.get('command')
            print(f'Received message from client {self.client_id} with command: {command}')

            if command == self.START_ROUND:
                print(f'Received start round command from client {self.client_id}')
                await self.matchmaking_logic()
            elif command == self.START_TOURNAMENT:
                print(f'Received start tournament command from client {self.client_id}')
                await self.start_tournament()
            elif command == self.LIST_PLAYERS:
                await self.send_info_to_client(self.LIST_PLAYERS, self.list_of_player_channels)
            elif command == self.LIST_MATCHES:
                await self.send_info_to_client(self.LIST_MATCHES, self.list_of_matches)
            elif command == self.LIST_ROUNDS:
                await self.send_info_to_client(self.LIST_ROUNDS, self.list_of_rounds)
            else:
                await self.send_info_to_client(self.CMD_NOT_FOUND, text_data)

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON data: {e}")
        except Exception as e:
            print(f"Error in receive method: {e}")
# ---------------------------------------

# Messaging methods
    async def broadcast(self, event):
        command = event['command']
        data = event['data']
        await self.send(text_data=json.dumps({
            'type': command,
            'data': data
        }))

    async def broadcast_to_group(self, group_name, command, data):
        await self.channel_layer.group_send(
            group_name,
            {
                'type': 'broadcast',
                'command': command,
                'data': data
            }
        )

    async def message_another_player(self, player_id, command, data):
        await self.channel_layer.group_send(
            player_id,
            {
                'type': 'broadcast',
                'command': command,
                'data': data
            }
        )

    async def send_info_to_client(self, command, data):
        print(f'Sending message to client {self.client_id} with data: {data}')
        await self.send(text_data=json.dumps({
            'type': command,
            'data': data
        }))
# ---------------------------------------

# Tournament Initialization
    async def start_tournament(self):
        try:
            await self.init_tour_object(self.tournament_id)
            await self.send_info_to_client('tournament_initialized', {})
            await self.broadcast_to_group(
                str(self.tournament_id),
                'tournament_initialized',
                {
                    'tournament_id': self.tournament_id,
                }
            )
        except Exception as e:
            print(f'Exception in start_tournament {e}')
# ---------------------------------------

# Round Generator
    async def matchmaking_logic(self):
        try:
            tournament = await self.get_tournament_object()
            if not tournament:
                raise ValueError("Tournament not found.")

            players = await self.get_tournament_players(tournament)
            if not players:
                raise ValueError("No players found for the tournament.")

            sit_out_player = self.get_sit_out_player(players)
            if not sit_out_player and len(players) % 2 != 0:
                raise ValueError("No sit-out player found for an odd number of players.")

            self.tournament_rounds_to_complete = max(1, math.ceil(math.log2(len(players))))

            if self.current_round >= self.tournament_rounds_to_complete:
                print('Tournament has ended')
                self.tournament_ended = True
                await self.save_tournament_results()
                print(f'Tournament {tournament} saved successfully')

                await self.broadcast_to_group(
                    self.tournament_id,
                    'tournament_info',
                    {
                        'tournament_id': self.tournament_id,
                        'matches': list(self.list_of_matches.keys()),
                        'rounds': list(self.list_of_rounds.keys()),
                        'total_rounds': self.tournament_rounds_to_complete,
                        'current_round': self.current_round,
                        'info': 'Tournament has ended.',
                    }
                )
                return
            
            sorted_players = sorted(players, key=lambda player: player.ELO, reverse=True)

            matches = await self.create_matches(sorted_players)
            self.list_of_matches = {match.id: match for match in matches}
            rounds = await self.create_round(tournament, matches, current_round=self.current_round)
            print(f'Matches and rounds created: {matches}, {rounds}')

            await database_sync_to_async(tournament.save)()
            print(f'Saved object tournament {tournament} saved successfully')

            matches_info = {
                str(match.id): {
                    'player1': match.player1.id,
                    'player2': match.player2.id,
                    'player1_score': match.player1_score,
                    'player2_score': match.player2_score,
                    'winner': match.winner.id if match.winner else None,
                    'date_played': match.date_played.isoformat() if match.date_played else None,
                    'active': match.active,
                }
                for match in matches
            }

            # Broadcast the modified match_data
            await self.broadcast_to_group(
                str(self.tournament_id),
                'matchmaking_info',
                {
                    'sit_out_player': sit_out_player.id if sit_out_player else None,
                    'matches': matches_info,
                    'rounds': list(self.list_of_rounds.keys()),
                    'total_rounds': self.tournament_rounds_to_complete,
                    'current_round': self.current_round + 1,
                }
            )
            
            self.current_round += 1
            print(f'Round launched next round is: {self.current_round}')

        except ValueError as ve:
            print(f"ValueError in matchmaking_logic: {ve}")
            # Log the error using the logger module
            logging.error(f"ValueError in matchmaking_logic: {ve}")
        except Exception as e:
            print(f"Error in matchmaking_logic: {e}")
            # Log the error using the logger module
            logging.error(f"Error in matchmaking_logic: {e}")
# ---------------------------------------


# Object Getters
    async def get_tournament_object(self):
        try:
            Tournament = import_string('api.tournament.models.Tournament')
            tournament = await database_sync_to_async(Tournament.objects.get)(pk=self.tournament_id)
            print(f'Found tournament with info {tournament}')
            return tournament

        except Tournament.DoesNotExist:
            print(f'Tournament with id {self.tournament_id} does not exist.')
            raise

        except Exception as e:
            print(f'Error getting tournament: {str(e)}')
            raise

    async def get_tournament_players(self, tournament):
        # Extract the logic for retrieving tournament players
        players = await database_sync_to_async(list)(tournament.players.all())
        print(f'Found players with info {players}')
        return players
# ---------------------------------------

# Matchmaking Helper Methods
    def get_sit_out_player(self, players):
        # Extract the logic for determining the sit-out player
        sit_out_player = random.choice(players) if len(players) % 2 != 0 else None
        print(f'Sit out player is {sit_out_player}')
        return sit_out_player

    def get_player_role(self, match):
        if match.player1.id == self.client_id:
            return 'player1'
        elif match.player2.id == self.client_id:
            return 'player2'
        else:
            return None

    @database_sync_to_async
    def calculate_player_score(self, player_id):
        print(f'Calculating score for player {player_id}')
        try:
            player_score = 0

            if self.list_of_rounds:
                for round_number, round_obj in self.list_of_rounds.items():
                    matches = round_obj.matches.filter(Q(player1=player_id) | Q(player2=player_id))

                    for match in matches:
                        if match.winner == player_id:
                            player_score += 1

            print(f'Player score for {player_id} is {player_score}')
            return player_score

        except Exception as e:
            print(f'Error calculating player score: {e}')
            return 0
# ---------------------------------------

# Object initialization/save methods
    @database_sync_to_async
    def create_matches(self, sorted_players):
        from api.tournament.models import Match
        matches = []
        num_players = len(sorted_players)

        # Adjust the range to handle odd number of players
        for i in range(0, num_players - 1, 2):
            player1 = sorted_players[i]
            player2 = sorted_players[i + 1]

            player1_score = 0
            player2_score = 0
            winner = None

            match = Match(
                player1=player1,
                player2=player2,
                player1_score=player1_score,
                player2_score=player2_score,
                winner=winner,
                date_played=timezone.now(),
                active=True
            )

            match.save()
            matches.append(match)
            self.list_of_matches[match.id] = match

        return matches

    @database_sync_to_async
    def create_round(self, tournament, matches, current_round=None):
        from api.tournament.models import Round
        print(f'Creating round for tournament {tournament}')
        new_round = Round(tournament=tournament, round_number=current_round)
        new_round.save()

        new_round.matches.set(matches)
        new_round.save()

        print(f'Round {new_round} saved successfully')
        self.list_of_rounds[new_round.id] = new_round

        return new_round

    @database_sync_to_async
    def init_player_obj(self, pk):
        try:
            User = import_string('api.userauth.models.CustomUser')
            user = get_object_or_404(User, pk=pk)
            if user is None:
                print(f'Could not find user with id {pk}')
                return None
            print(f'Found user with info {user}')
            self.player_object = user
            self.list_of_player_objects[self.client_id] = self.player_object
            self.list_of_player_channels[self.client_id] = self.channel_name
            return user
        except Exception as e:
            print(e)
            return None

    @database_sync_to_async
    def init_tour_object(self, pk):
        try:
            Tournament = import_string('api.tournament.models.Tournament')
            tournament = get_object_or_404(Tournament, pk=pk)

            if tournament is None:
                print(f'Could not find tournament with id {pk}')
                return None
            
            print(f'Found tournament with info {tournament}')
            tournament.players.add(self.player_object)
            tournament.tournament_admin = self.player_object
            tournament.save()

            self.tournament_object = tournament
            self.tournament_admin_id = self.client_id

            self.list_of_player_objects = {player.id: player for player in tournament.players.all()}

        except Exception as e:
            print(e)
            print(f'Could not find tournament with id {pk}')
            return None

    @database_sync_to_async
    def save_tournament_results(self):
        try:
            Tournament = import_string('api.tournament.models.Tournament')
            tournament = get_object_or_404(Tournament, pk=self.tournament_id)

            for match in self.list_of_matches.values():
                match.save()

            for round in self.list_of_rounds.values():
                round.save()

            for player in self.list_of_player_objects.values():
                player.ELO = self.player_score
                player.save()

            tournament.round = self.current_round
            
            tournament.save()
        
        except Exception as e:
            print(f'Error saving tournament results: {e}')
            return None
# ---------------------------------------
