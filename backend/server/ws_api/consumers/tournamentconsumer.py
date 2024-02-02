import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.shortcuts import get_object_or_404
from django.utils import timezone
import random
import logging
import asyncio
from api.jwt_utils import get_user_id_from_jwt_token
from django.utils.module_loading import import_string

class TournamentConsumer(AsyncWebsocketConsumer):

    connected_clients = set()  # Class-level variable to store connected clients
    tournament_ready = {}      # Class-level variable to store tournaments ready status

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = None                   # Client ID
        self.player_object = None               # Player object
        self.player_score = 0                   # Player score to keep track of ELO
        self.tournament_id = None               # Tournament ID unique to each tournament
        self.tournament_ended = False           # Flag to indicate if the tournament has ended
        self.current_round = 0                  # Current round of the tournament
        self.tournament_admin_id = None         # Tournament admin ID - admin can start the tournament
        self.tournament_object = None           # Tournament object - contains all the tournament info
        self.tournament_rounds_to_complete = 2  # Number of rounds to complete the tournament
        self.list_of_matches = {}               # List of matches during the entire tournament
        self.list_of_rounds = {}                # List of rounds during the entire tournament
        self.list_of_registered_players = {}    # List of registered players for the tournament
        self.match_monitor_task = None          # Task to monitor the matches
        self.tournament_name = None             # Name of tournament


# Define constants for commands
    START_ROUND = 'start_round'
    LIST_PLAYERS = 'list_players'
    CMD_NOT_FOUND = 'command_not_found'
    CLOSE_CONNECTION = 'close_connection'
# ---------------------------------------

# Class methods
    @classmethod
    def add_connected_client(cls, client_id):
        cls.connected_clients.add(client_id)

    @classmethod
    def remove_connected_client(cls, client_id):
        cls.connected_clients.discard(client_id)

    @classmethod
    def get_connected_clients(cls):
        return list(cls.connected_clients)
# ---------------------------------------

# Channel methods (Connect, Disconnect, Receive)
    async def connect(self):
        query_string = self.scope['query_string'].decode('utf-8')
        query_params = parse_qs(query_string)
        self.tournament_id = self.scope['url_route']['kwargs']['tournament_id']
        token = query_params['token'][0]

        self.client_id = self.verifty_user_via_token(token)

        # Get the user and see if they exist before accepting the connection
        user = await self.init_player_obj(self.client_id)
        tournament = await self.init_tour_obj(self.tournament_id)
        print(f'Player object: {self.player_object} and tournament object: {self.tournament_object}')

        if TournamentConsumer.tournament_ready.get(self.tournament_id) == True:
            await self.close()

        await self.accept()

        # If the user or tournament does not exist, close the connection
        if user is None or tournament is None:
            await self.send_info_to_client("error", "tournament_not_found")
            await self.close()
            return
        
        # Add client to the group channel
        print(f'Adding {self.client_id} to group {self.tournament_id}')
        await self.channel_layer.group_add(self.tournament_id, self.channel_name)
        await self.channel_layer.group_add(self.client_id, self.channel_name)

        # Add client to class-level variable to keep track of connected clients
        self.add_connected_client(self.client_id)

        TournamentConsumer.tournament_ready[self.tournament_id] = False
        await self.broadcast_to_group(
            str(self.tournament_id),
            'player_joined',
            {
                'tournament_id': self.tournament_id,
                'player_id': self.client_id,
                'registered_players': self.list_of_registered_players,
                'tournament_admin_id': self.tournament_admin_id,
                'tournament_name': self.tournament_name
            }
        )

        # If we have 4 players, close the tournament and start the tournament otherwise just announce the new player
        if len(self.list_of_registered_players) == 4:
            TournamentConsumer.tournament_ready[self.tournament_id] = True
            await self.broadcast_to_group(
                str(self.tournament_id),
                'tournament_ready',
                {
                    'tournament_id': self.tournament_id,
                    'registered_players': self.list_of_registered_players,
                    'tournament_admin_id': self.tournament_admin_id,
                }
            )
            # await asyncio.sleep(5)
            await self.receive(json.dumps({'command': self.START_ROUND}))

    async def disconnect(self, close_code):
        try:
            print(f'Client {self.client_id} disconnected with code {close_code}')
            # Remove client from the group channel
            await self.channel_layer.group_discard(str(self.tournament_id), self.channel_name)
            await self.channel_layer.group_discard(str(self.client_id), self.channel_name)

            # Remove client from class-level variable to keep track of connected clients
            self.remove_connected_client(self.client_id)

            # If the tournament has ended, close the connection
            if self.tournament_ended:
                await self.close()
                return

            await self.broadcast_to_group(
                str(self.tournament_id),
                'player_disconnected',
                {
                    'tournament_id': self.tournament_id,
                    'info': 'Tournament ended',
                })
            if self.match_monitor_task:
                self.match_monitor_task.cancel()
            await self.delete_tournament()
            await self.close()
                
            

            # If the tournament has not ended, check if the client is the tournament admin
            # if self.client_id == str(self.tournament_admin_id):
            #     print(f'Tournament admin {self.client_id} disconnected')
            #     await self.assign_new_tournament_admin()
            #     await self.broadcast_to_group(
            #         str(self.tournament_id),
            #         'tournament_admin_disconnected',
            #         {
            #             'tournament_id': self.tournament_id,
            #             'new_admin': self.tournament_admin_id,
            #             'info': 'Tournament admin disconnected.',
            #         }
            #     )
            # else:
            #     print(f'Player {self.client_id} disconnected')
            #     await self.broadcast_to_group(
            #         str(self.tournament_id),
            #         'player_disconnected',
            #         {
            #             'tournament_id': self.tournament_id,
            #             'player_id': self.client_id,
            #             'info': 'Player disconnected.',
            #         }
            #     )
            # if self.tournament_admin_id is None:
            #     await self.delete_tournament()
            #     await self.broadcast_to_group(
            #         str(self.tournament_id),
            #         'tournament_deleted',
            #         {
            #             'tournament_id': self.tournament_id,
            #             'info': 'Tournament deleted.',
            #         }
            #     )
            #     await self.close()
            #     return
            # await self.close()
            # return
        except Exception as e:
            print(f"Error in disconnect method: {e}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            command = data.get('command')

            if command == self.START_ROUND:
                if TournamentConsumer.tournament_ready[self.tournament_id] and self.tournament_ended == False:
                    await self.matchmaking_logic()
                    TournamentConsumer.tournament_ready[self.tournament_id] = False
                    if not self.tournament_ended:
                        self.match_monitor_task = asyncio.create_task(self.check_match_finished())
                        # asyncio.create_task(self.check_match_finished())
                else:
                    await self.send_info_to_client("message", "You are not the tournament admin or the tournament is not ready to start.")
                    print(f'Client {self.client_id} is not the tournament admin. Tournament ready status: {TournamentConsumer.tournament_ready[self.tournament_id]}. Tournament ended: {self.tournament_ended}')
            elif command == self.CLOSE_CONNECTION:
                await self.disconnect(1000)
            elif command == self.LIST_PLAYERS:
                list_of_current_players = self.get_connected_clients()
                await self.send_info_to_client(self.LIST_PLAYERS, list_of_current_players)
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

# Round Generator
    async def matchmaking_logic(self):
        try:
            # Check if the tournament has ended
            if self.tournament_ended or not list(self.list_of_registered_players):
                print(f"Tournament has ended: {self.tournament_ended}")
                return

            if self.current_round >= self.tournament_rounds_to_complete:
                print('Tournament has ended')
                self.tournament_ended = True

                await self.save_tournament_results()

                await self.broadcast_to_group(
                    self.tournament_id,
                    'tournament_ended',
                    {
                        'tournament_id': self.tournament_id,
                        'total_rounds': self.tournament_rounds_to_complete,
                        'current_round': self.current_round,
                        'tournament_winner': self.list_of_registered_players,
                        'info': 'Tournament has ended.',
                    }
                )
                return

            matches = await self.create_matches(list(self.list_of_registered_players))
            print(f'Matches created: {matches}')

            self.list_of_matches = {match.id: match for match in matches}
            print(f'List of matches: {self.list_of_matches}')

            rounds = await self.create_round(matches, current_round=self.current_round)
            print(f'Matches and rounds created: {matches}, {rounds}')

            matches_info = {
                str(match.id): {
                    'match_id': match.id,
                    'player1': match.player1.id,
                    'player2': match.player2.id,
                    'active': match.active,
                }
                for match in matches
            }

            # Broadcast the modified match_data
            await self.broadcast_to_group(
                str(self.tournament_id),
                'matchmaking_info',
                {
                    'matches': matches_info,
                    'rounds': list(self.list_of_rounds.keys()),
                    'total_rounds': self.tournament_rounds_to_complete,
                    'current_round': self.current_round + 1,
                }
            )

            self.current_round += 1
            print(f'Round launched next round is: {self.current_round}, Matches played so far: {self.list_of_matches}')

        except ValueError as ve:
            print(f"ValueError in matchmaking_logic: {ve}")
            # Log the error using the logger module
            logging.error(f"ValueError in matchmaking_logic: {ve}")
            await self.disconnect()
        except Exception as e:
            print(f"Error in matchmaking_logic: {e}")
            # Log the error using the logger module
            logging.error(f"Error in matchmaking_logic: {e}")
            await self.disconnect()
# ---------------------------------------

# Matchmaking Helper Methods
    async def check_match_finished(self):
        start_time = timezone.now()
        try:
            # This coroutine will loop through the matches and once they are all complete will set the tournament_ready flag to True
            while True:
                await asyncio.sleep(1)
                matches_finished = True
                for match in self.list_of_matches.values():
                    print(f"Checking if the mathces in {self.list_of_matches} are finished. Currently checking match {match}")
                    active = await self.check_match_status(match.id)
                    if active:
                        print(f"Match {match} is active")
                        matches_finished = False
                        break

                if matches_finished:
                    print('Matches are finished')
                    await self.kick_losers()
                    TournamentConsumer.tournament_ready[self.tournament_id] = True
                    await self.broadcast_to_group(
                        str(self.tournament_id),
                        'matches_finished',
                        {
                            'tournament_id': self.tournament_id,
                            'info': 'Matches are finished.',
                            'registered_players': self.list_of_registered_players,
                        }
                    )
                    # To avoid admin trolling, we will wait for 5 seconds before starting the next round
                    await asyncio.sleep(5)
                    await self.receive(json.dumps({'command': self.START_ROUND}))
                    break

        except asyncio.CancelledError as ce:
            print(f"CancelledError in check_match_finished: {ce}")
            await self.disconnect()
        except ValueError as ve:
            print(f"ValueError in matchmaking_logic: {ve}")
            await self.disconnect()
        except Exception as e:
            print(f"Error in matchmaking_logic: {e}")
            await self.disconnect()

    @database_sync_to_async
    def check_match_status(self, match_id):
        try:
            from api.tournament.models import Match
            match = get_object_or_404(Match, pk=match_id)

            if match is None:
                print(f'Could not find match with id {match_id}')
                return None

            return bool(match.active)
        except Exception as e:
            print(f'Error checking match status: {e}')
            return None

    @database_sync_to_async
    def kick_losers(self):
        try:
            from api.tournament.models import Match
            from api.userauth.models import CustomUser as User
            from api.tournament.models import Tournament

            tournament = Tournament.objects.get(pk=self.tournament_id)
            print(f'Kicking losers for tournament {tournament}')

            # Clear the list of registered players
            self.list_of_registered_players = []

            # Check previous matches and remove the losers from the registerd player list not the tournament model. So the tournament model will still have the losers but they will not be able to play in the next round.
            for match in self.list_of_matches.values():
                # Get the updated match object
                match = Match.objects.get(pk=match.id)
                print(f'Checking match {match}')
                if match.winner:
                    print(f'Winner is {match.winner}')
                    # Add winner to the list of registered players
                    self.list_of_registered_players.append({
                        'id': match.winner.id,
                        'username': match.winner.username,
                    })
                    print(f'Updated list of registered players: {self.list_of_registered_players}') 
                else:
                    print(f'Match {match} has no winner')
                    return None

            print(f'Kicked losers successfully, remaining players: {self.list_of_registered_players}')

            return True

        except Exception as e:
            print(f'Error kicking losers: {e}')
            return None

    @database_sync_to_async
    def assign_new_tournament_admin(self):
        try:
            from api.tournament.models import Tournament
            tournament = Tournament.objects.get(pk=self.tournament_id)
            print(f'Assigning new tournament admin for tournament {tournament}')

            players = tournament.players.all()
            print(f'Players in tournament {players}')

            # Check which players are actually connected and assign the first one as the new tournament admin
            for player in players:
                if str(player.id) in self.get_connected_clients():
                    self.tournament_admin_id = player.id
                    tournament.save()
                    print(f'New tournament admin is {self.tournament_admin_id}')
                    return self.tournament_admin_id

            print('Could not find a new tournament admin')
            self.tournament_ended = True
            self.tournament_admin_id = None
            return None

        except Exception as e:
            print(f'Error assigning new tournament admin: {e}')
            return None    
# ---------------------------------------

# Object initialization/save methods
    @database_sync_to_async
    def create_matches(self, sorted_players):
        from api.tournament.models import Match
        from api.userauth.models import CustomUser as User

        matches = []
        num_players = len(sorted_players)

        # Adjust the range to handle odd number of players
        for i in range(0, num_players - 1, 2):
            player1_data = sorted_players[i]
            player2_data = sorted_players[i + 1]
            print(f'Creating match between {player1_data} and {player2_data}')

            player1 = User.objects.get(pk=player1_data['id'])
            player2 = User.objects.get(pk=player2_data['id'])
            print(f'Player 1: {player1} and Player 2: {player2}')

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
    def create_round(self, matches, current_round=None):
        from api.tournament.models import Round
        from api.tournament.models import Tournament

        tournament = Tournament.objects.get(pk=self.tournament_id)
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

            return True

        except Exception as e:
            print(e)
            return None

    @database_sync_to_async
    def init_tour_obj(self, pk):
        try:
            Tournament = import_string('api.tournament.models.Tournament')
            self.tournament_object = get_object_or_404(Tournament, pk=pk)

            if self.tournament_object is None:
                print(f'Could not find tournament with id {pk}')
                return None
            
            # Extracting relevant information from CustomUser objects
            self.list_of_registered_players = list(self.tournament_object.players.all().values('id', 'username'))
            self.tournament_admin_id = self.tournament_object.tournament_admin.id if self.tournament_object.tournament_admin else None  
            self.current_round = self.tournament_object.round
            self.tournament_name = self.tournament_object.name
            
            # The admin will always be in the list of registered players. We will accept new players till there are 4 players. At that point we close the tournament and kick out any new players.
            # If there are less than 4 players new clients will be added to the tournament object and we will save the tournament object.
            if len(self.list_of_registered_players) <= 4 and self.tournament_object.joinable:
                self.tournament_object.players.add(self.player_object)
                self.tournament_object.save()
                self.list_of_registered_players = list(self.tournament_object.players.all().values('id', 'username'))
                if len(self.list_of_registered_players) == 4:
                    self.tournament_object.joinable = False
                    self.tournament_object.save()
                    print(f'Tournament {self.tournament_id} is now closed. No new players can join.')
                
            print(f'List of registered players: {self.list_of_registered_players} and tournament admin id: {self.tournament_admin_id}')

            # Check if the client is in the list of registered players
            if self.client_id not in [str(player['id']) for player in self.list_of_registered_players]:
                print(f'Client {self.client_id} not registered for tournament {self.tournament_id}')
                return None
            
            return True

        except Exception as e:
            print(e)
            print(f'Could not find tournament with id {pk}')
            return None

    @database_sync_to_async
    def save_tournament_results(self):
        try:
            Tournament = import_string('api.tournament.models.Tournament')
            User = import_string('api.userauth.models.CustomUser')
            tournament = get_object_or_404(Tournament, pk=self.tournament_id)
            winner = get_object_or_404(User, pk=self.list_of_registered_players[0]['id'])

            # Save the tournament results
            tournament.winner = winner
            tournament.end_date = timezone.now()
            tournament.save()
        
        except Exception as e:
            print(f'Error saving tournament results: {e}')
            return None

    @database_sync_to_async
    def delete_tournament(self):
        try:
            print(f'Deleting tournament {self.tournament_id}')
            Tournament = import_string('api.tournament.models.Tournament')
            Round = import_string('api.tournament.models.Round')
            tournament = get_object_or_404(Tournament, pk=self.tournament_id)
            
            # Delete the round associated with the tournament and the matches withing the round since rounds are saved as ints to avoid circular dependency we need to import the Round model here
            print(f'Rounds to delete: {self.list_of_rounds}')
            rounds_list = tournament.rounds.all()
            for round in rounds_list:
                print(f'Deleting round {round}')
                round.delete()
         
            tournament.delete()
            return True
        except Exception as e:
            print(f'Error deleting tournament: {e}')
            return None
# ---------------------------------------

# Helper methods
    def verifty_user_via_token(self, token):
        try:
            user_id = get_user_id_from_jwt_token(token)
            print(f'Verified user with id {user_id}')
            return str(user_id)
        except Exception as e:
            print(f'Error verifying user: {e}')
            return None