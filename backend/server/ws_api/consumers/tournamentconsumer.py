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

from django.utils.module_loading import import_string



class TournamentConsumer(AsyncWebsocketConsumer):
    list_of_player_channels = {}
    list_of_player_objects = {}
    list_of_matches = {}
    list_of_rounds = {}
    tournament_admin_id = None
    tournament_object = None
    tournament_ended = False
    tournament_rounds_to_complete = 0

    # Define constants for commands
    START_TOURNAMENT = 'start_tournament'
    START_MATCH = 'start_match'
    END_MATCH = 'end_match'
    START_ROUND = 'start_round'
    END_ROUND = 'end_round'
    ADD_PLAYER = 'add_player'
    REMOVE_PLAYER = 'remove_player'
    LIST_PLAYERS = 'list_players'
    LIST_MATCHES = 'list_matches'
    LIST_ROUNDS = 'list_rounds'


# Channel methods (Connect, Disconnect, Receive)
    async def connect(self):
        query_string = self.scope['query_string'].decode('utf-8')
        query_params = parse_qs(query_string)
        self.tournament_id = self.scope['url_route']['kwargs']['tournament_id']
        self.client_id = query_params['client_id'][0]

        # Get the user and see if they exist before accepting the connection
        self.player_object = await self.get_user(self.client_id)
        if self.player_object is None:
            await self.close()
            return

        await self.accept()

        # Add client to the group channel
        print(f'Adding {self.client_id} to group {self.tournament_id}')
        await self.channel_layer.group_add(
            str(self.tournament_id),
            self.channel_name
        )

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
        # Remove client from the group channel
        await self.channel_layer.group_discard(
            str(self.tournament_id),
            self.channel_name
        )
        # Remove client from the list of players or observers
        if self.client_id in self.list_of_player_channels:
            del self.list_of_player_channels[self.client_id]

        # Send info of group status every time a client leaves
        await self.broadcast_to_group(
            str(self.tournament_id),
            'tournament_info',
            {
                'tournament_id': self.tournament_id,
                'players': self.list_of_player_channels,
                'matches': self.list_of_matches,
                'rounds': self.list_of_rounds,
                'tournament_admin_id': self.tournament_admin_id
            }
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            command = data.get('command')
            print(f'Received message from client {self.client_id} with command: {command}')

            if command == self.START_TOURNAMENT:
                await self.start_tournament()
            elif command == self.START_ROUND:
                await self.matchmaking_logic()

            # elif command == self.LIST_PLAYERS:
            #     await self.send_info_to_client(self.LIST_PLAYERS, self.list_of_player_channels)
            # elif command == self.LIST_MATCHES:
            #     await self.send_info_to_client(self.LIST_MATCHES, self.list_of_matches)
            # elif command == self.LIST_ROUNDS:
            #     await self.send_info_to_client(self.LIST_ROUNDS, self.list_of_rounds)
            else:
                print(f"Unknown command: {command}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON data: {e}")
        except Exception as e:
            print(f"Error in receive method: {e}")
# ---------------------------------------


# Messaging methods
    async def broadcast(self, event):
        command = event['command']
        data = event['data']
        print(f'Sending message to client {self.client_id} with data: {data}')
        await self.send(text_data=json.dumps({
            'type': command,
            'data': data
        }))

    async def broadcast_to_group(self, group_name, command, data):
        print(f'Channel Broadcasting {command} to group {group_name}')
        await self.channel_layer.group_send(
            group_name,
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

# Game methods
    async def start_tournament(self):
        await self.get_tournament(self.tournament_id)
        await self.send_info_to_client('tournament_initialized', {})
        await self.broadcast_to_group(
            str(self.tournament_id),
            'tournament_info',
            {
                'tournament_id': self.tournament_id,
                'players_in_websocket': self.list_of_player_channels,
                'matches': self.list_of_matches,
                'rounds': self.list_of_rounds,
                'tournament_admin_id': self.tournament_admin_id,
            }
        )

    async def matchmaking_logic(self):
        try:
            Tournament = import_string('api.tournament.models.Tournament')
            print('Running matchmaking logic')

            tournament = await database_sync_to_async(Tournament.objects.get)(pk=self.tournament_id)
            print(f'Found tournament with info {tournament}')

            players = await database_sync_to_async(list)(tournament.players.all())
            print(f'Found players with info {players}')

            if players.count() % 2 != 0:
                sit_out_player = random.choice(players)
            else:
                sit_out_player = None

            print(f'Sit out player is {sit_out_player}')

            self.tournament_rounds_to_complete = math.ceil(math.log2(players.count()))
            if tournament.round >= self.tournament_rounds_to_complete:
                winner = max(players, key=lambda player: self.calculate_player_score(player, tournament=tournament))
                tournament.winner = winner
                tournament.end_date = timezone.now()
                tournament.save()
                self.broadcast_to_group(
                    str(self.tournament_id),
                    'tournament_info',
                    {
                        'tournament_id': self.tournament_id,
                        'players': self.list_of_player_channels,
                        'matches': self.list_of_matches,
                        'rounds': self.list_of_rounds,
                        'tournament_admin_id': self.tournament_admin_id,
                        'winner': winner,
                    }
                )
                return

            if tournament.round == 0:
                sorted_players = sorted(players, key=lambda player: player.ELO, reverse=True)
            else:
                sorted_players = sorted(players, key=lambda player: self.calculate_player_score(player, tournament=tournament), reverse=True)
            
            matches = self.create_matches(sorted_players)
            self.list_of_matches = {match.id: match for match in matches}
            self.create_round(tournament, matches)

            tournament.save()

            # Prepare the response with match details
            match_data = []
            for match in matches:
                # Use a helper function to determine player role
                role = self.get_player_role(match)
                if role:
                    match_info = {
                        'match_id': match.id,
                        'current_round': tournament.round,
                        'total_rounds': self.tournament_rounds_to_complete,
                        'player1_id': match.player1.id,
                        'player2_id': match.player2.id,
                        'your_role': role,
                    }
                    match_data.append(match_info)

            # Broadcast the modified match_data
            self.broadcast_to_group(
                str(self.tournament_id),
                'matchmaking_info',
                {
                    'sit_out_player': sit_out_player,
                    'matches': match_data,
                }
            )

        except Exception as e:
            # Handle specific exceptions as needed
            print(str(e))
# ---------------------------------------

# Creation methods
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

        return matches

    def create_round(self, tournament, matches):
        from api.tournament.models import Round
        new_round = Round(tournament=tournament, round_number=tournament.round + 1)
        new_round.save()
        new_round.matches.set(matches)
# ---------------------------------------

# Helper methods
    def calculate_player_score(self, player, tournament=None):
        if not tournament:
            return 0

        latest_round = tournament.rounds.last()  # Get the latest round

        if latest_round:
            matches = latest_round.matches.filter(Q(player1=player) | Q(player2=player))
            player_score = sum(1 for match in matches if match.winner == player)
        else:
            player_score = 0

        return player_score

    def get_player_role(self, match):
        if match.player1.id == self.client_id:
            return 'player1'
        elif match.player2.id == self.client_id:
            return 'player2'
        else:
            return None
# ---------------------------------------

# Getters
    @database_sync_to_async
    def get_user(self, pk):
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
    def get_tournament(self, pk):
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
# ---------------------------------------
