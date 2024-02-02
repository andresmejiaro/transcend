from channels.generic.websocket import AsyncWebsocketConsumer
import json                                                 # Used to encode and decode JSON data
import asyncio
import time
import random
from urllib.parse import parse_qs                           # Used to parse the query string
from channels.db import database_sync_to_async              # Used to make database calls asynchronously
from django.shortcuts import get_object_or_404              # Used to get an object from the database
from django.http import Http404                             # Used to return a 404 error if an object is not found
from django.utils import timezone                           # Used to get the current time
from django.db import transaction                           # Used to make database transactions used for friendship model
from django.utils.module_loading import import_string       # Used to import models from other apps to avoid circular imports
import logging                                              # Used to log errors
from api.jwt_utils import get_user_id_from_jwt_token

class LobbyConsumer(AsyncWebsocketConsumer):

# Class variables shared by all instances
    list_of_admins = {}
    list_of_online_users = {}
    queue = {}
    tournament = {}
    lobby_name = 'lobby'

# Endpoints and commands (Client -> Server)
    LIST_OF_USERS = 'list_of_users'                     # Command to send the list of online users (Connected to the socket)
    LIST_SENT_INVITES = 'list_sent_invites'             # Command to send the list of invites sent
    LIST_RECEIVED_INVITES = 'list_received_invites'     # Command to send the list of invites received
    SEND_PRV_MSG = 'send_prv_msg'                       # Command to send a private message arguments: pass the values as of 'client_id' and 'message' eg: {'command': 'send_prv_msg', 'data': {'client_id': '1', 'message': 'Hello'}}
    SEND_NOTIFICATION = 'send_notification'             # Command to send a group wide notification arguments: pass the values as of 'message' eg: {'command': 'send_notification', 'data': {'message': 'Hello'}}
    CMD_NOT_FOUND = 'command_not_found'                 # Command to send when a command is not found
    CLOSE_CONNECTION = 'close_connection'               # Command to close the connection
    CREATE_USER = 'create_user'                         # Command to create a user arguments: pass the values as of 'user_data'
    MODIFY_USER = 'modify_user'                         # Command to modify a user arguments: pass the values as of 'changes'
    SERVER_TIME = 'server_time'                         # Command to send the server time
    INVITE_TO_MATCH = 'invite_to_match'                 # Command to invite a user to a match arguments: pass the values as of 'client_id' and 'match_id' eg: {'command': 'invite_to_match', 'data': {'client_id': '1', 'match_id': '1'}}
    ACCEPT_MATCH = 'accept_match'                       # Command to accept a match arguments: pass the values as of 'client_id' and 'match_id' eg: {'command': 'accept_match', 'data': {'client_id': '1', 'match_id': '1'}}
    REJECT_MATCH = 'reject_match'                       # Command to reject a match arguments: pass the values as of 'client_id' and 'match_id' eg: {'command': 'reject_match', 'data': {'client_id': '1', 'match_id': '1'}}
    CANCEL_MATCH = 'cancel_match'                       # Command to cancel a match arguments: pass the values as of 'client_id' and 'match_id' eg: {'command': 'cancel_match', 'data': {'client_id': '1', 'match_id': '1'}}
    SEND_FRIEND_REQUEST = 'send_friend_request'         # Command to send a friend request arguments: pass the values as of 'client_id' eg: {'command': 'send_friend_request', 'data': {'client_id': '1'}}
    ACCEPT_FRIEND_REQUEST = 'accept_friend_request'     # Command to accept a friend request arguments: pass the values as of 'client_id' eg: {'command': 'accept_friend_request', 'data': {'client_id': '1'}}
    REJECT_FRIEND_REQUEST = 'reject_friend_request'     # Command to reject a friend request arguments: pass the values as of 'client_id' eg: {'command': 'reject_friend_request', 'data': {'client_id': '1'}}
    CANCEL_FRIEND_REQUEST = 'cancel_friend_request'     # Command to cancel a friend request arguments: pass the values as of 'client_id' eg: {'command': 'cancel_friend_request', 'data': {'client_id': '1'}}
    GET_USER_INFO = 'get_user_info'                     # Command to get user info arguments: pass the values as of 'client_id' eg: {'command': 'get_user_info', 'data': {'client_id': '35'}}
    INVITE_TO_TOURNAMENT = 'invite_to_tournament'       # Command to invite a user to a tournament arguments: pass the values as of 'client_id' and 'tournament_id' eg: {'command': 'invite_to_tournament', 'data': {'client_id': '1', 'tournament_id': '1'}}
    ACCEPT_TOURNAMENT = 'accept_tournament'             # Command to accept a tournament arguments: pass the values as of 'client_id' and 'tournament_id' eg: {'command': 'accept_tournament', 'data': {'client_id': '1', 'tournament_id': '1'}}
    REJECT_TOURNAMENT = 'reject_tournament'             # Command to reject a tournament arguments: pass the values as of 'client_id' and 'tournament_id' eg: {'command': 'reject_tournament', 'data': {'client_id': '1', 'tournament_id': '1'}}
    CANCEL_TOURNAMENT = 'cancel_tournament'             # Command to cancel a tournament arguments: pass the values as of 'client_id' and 'tournament_id' eg: {'command': 'cancel_tournament', 'data': {'client_id': '1', 'tournament_id': '1'}}
    JOIN_QUEUE = 'join_queue'                           # Command to join the queue arguments: pass the values as of 'client_id' eg: {'command': 'join_queue', 'data': {'queue_name': 'global'}}
    LEAVE_QUEUE = 'leave_queue'                         # Command to leave the queue arguments: pass the values as of 'client_id' eg: {'command': 'leave_queue', 'data': {'queue_name': 'tournament_26'}}
    CREATE_3v3 = 'create_tournament'                    # Command to create a 3v3 match arguments: pass the values as of 'client_id' eg: {'command': 'create_3v3', 'data': {"tournament_name": "cawabonga"}}
    JOIN_3v3 = 'join_tournament'                        # Command to join a 3v3 match arguments: pass the values as of 'client_id' eg: {'command': 'join_3v3'}
    START_3v3 = 'start_tournament'                      # Command to start a 3v3 match arguments: pass the values as of 'client_id' eg: {'command': 'start_3v3'}
    NEXT_MATCH = 'next_match'                           # Command to get the next match or winner arguments: pass the values as of 'client_id' eg: {'command': 'next_match'}
# ---------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = None
        self.client_username = None

# Matchmaking methods
    async def join_queue(self, queue_name, user_id):
        try:
            if self.queue.get(queue_name) is None:
                LobbyConsumer.queue[queue_name] = []
            if user_id in LobbyConsumer.queue[queue_name]:
                await self.send_info_to_client(
                    'joined_queue',
                    {
                        'time': timezone.now().isoformat(),
                        'client_id': user_id,
                        'queue_name': queue_name,
                        'message': 'Already in queue',
                    }
                )
                return
            LobbyConsumer.queue[queue_name].append(user_id)
            await self.send_info_to_client(
                'joined_queue',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': user_id,
                    'queue_name': queue_name,
                    'message': 'Joined queue successfully',
                }
            )
            await self.find_opponent(queue_name, user_id)
        except Exception as e:
            print(f'Exception in join_queue {e}')
            await self.disconnect(1000)
            
    async def leave_queue(self, queue_name, user_id):
        try:
            if LobbyConsumer.queue.get(queue_name) is None:
                await self.send_info_to_client(
                    'left_queue',
                    {
                        'time': timezone.now().isoformat(),
                        'client_id': user_id,
                        'queue_name': queue_name,
                        'message': 'Queue does not exist',
                    }
                )
            if user_id not in LobbyConsumer.queue[queue_name]:
                await self.send_info_to_client(
                    'left_queue',
                    {
                        'time': timezone.now().isoformat(),
                        'client_id': user_id,
                        'queue_name': queue_name,
                        'message': 'Not in queue',
                    }
                )
                return
            LobbyConsumer.queue[queue_name].remove(user_id)
            await self.send_info_to_client(
                'left_queue',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': user_id,
                    'queue_name': queue_name,
                    'message': 'Left queue successfully',
                }
            )
        except Exception as e:
            print(f'Exception in leave_queue {e}')
            await self.disconnect(1000)

    async def find_opponent(self, queue_name, user_id):
        try:
            # while len(self.queue[queue_name]) < 2 and user_id in self.queue[queue_name]:
            #     await asyncio.sleep(1)
            if len(self.queue[queue_name]) != 2:
                return
            
            if user_id not in self.queue[queue_name]:
                return
                
            if len(self.queue[queue_name]) >= 2:
                opponent_id = self.queue[queue_name][0]
                if opponent_id == user_id:
                    opponent_id = self.queue[queue_name][1]
                    
                match_id = await self.create_match(user_id, opponent_id)
                
                await self.send_info_to_client(
                    'found_opponent',
                    {
                        'time': timezone.now().isoformat(),
                        'client_id': user_id,
                        'opponent_id': opponent_id,
                        'match_id': match_id,
                        'message': 'Found opponent successfully',
                    }
                )
                await self.message_another_player(
                    opponent_id,
                    'found_opponent',
                    {
                        'time': timezone.now().isoformat(),
                        'client_id': opponent_id,
                        'opponent_id': user_id,
                        'match_id': match_id,
                        'message': 'Found opponent successfully',
                    }
                )
                await self.leave_queue(queue_name, user_id)
                await self.leave_queue(queue_name, opponent_id)
                    
                
        except Exception as e:
            print(f'Exception in find_opponent {e}')
            await self.disconnect(1000)
# ---------------------------------------

# Channel methods (Connect, Disconnect, Receive)
    async def connect(self):
        try:
            # Get the client id from the query string
            query_string = self.scope['query_string'].decode('utf-8')
            query_params = parse_qs(query_string)
            if not query_params.get('token'):
                await self.close()
            print(f'Token: {query_params.get("token")}')
            token = query_params['token'][0]

            try:
                user_id = get_user_id_from_jwt_token(token)
                self.client_id = str(user_id)
                print(self.client_id)
            except Exception as e:
                await self.close()

            if await self.does_not_exist(self.client_id):
                # print("WTF IS GOING ON")
                await self.message_another_player(
                    self.client_id,
                    'duplicate_connection',
                    {
                        'time': timezone.now().isoformat(),
                        'client_id': self.client_id,
                        'message': 'Duplicate connection',
                    }
                )
                await self.close()
                return

            await self.accept()

            # Channel layer groups
            await self.channel_layer.group_add(self.lobby_name, self.channel_name)
            await self.channel_layer.group_add(self.client_id, self.channel_name)

            # Predifined arrival method
            await self.announce_arrival()


        except Exception as e:
            error_message = f"Error in connect method: {e}"
            print(error_message)
            logging.error(error_message)
            await self.close()

    async def disconnect(self, close_code):
        try:
            print(f'Client {self.client_id} disconnected with code {close_code}')
            if self.list_of_online_users.get(self.client_id):
                del self.list_of_online_users[self.client_id]
                        # Remove client from the group channel
            await self.channel_layer.group_discard(self.lobby_name, self.channel_name)
            await self.channel_layer.group_discard(self.client_id, self.channel_name)


            for queue in LobbyConsumer.queue.keys():
                if self.client_id in LobbyConsumer.queue[queue]:
                    print(f"Leaving queue: {queue}")
                    LobbyConsumer.queue[queue].remove(self.client_id)

            # Send info of group status every time a client leaves
            await self.announce_departure()
            self.close()

        except Exception as e:
            error_message = f"Error in disconnect method: {e}"
            print(error_message)
            logging.error(error_message)
            await self.close()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            command = data.get('command')
            data = data.get('data')

            if command == self.LIST_OF_USERS:
                await self.send_info_to_client(self.LIST_OF_USERS, self.list_of_online_users)
            elif command == self.LIST_SENT_INVITES:
                await self.send_info_to_client(self.LIST_SENT_INVITES, await self.get_sent_invites(self.client_id))
            elif command == self.LIST_RECEIVED_INVITES:
                await self.send_info_to_client(self.LIST_RECEIVED_INVITES, await self.get_recieved_invites(self.client_id))
            elif command == self.CLOSE_CONNECTION:
                await self.disconnect(1000)
            elif command == self.SEND_PRV_MSG:
                await self.message_another_player(data['client_id'], 'prv_msg', data['message'])
            elif command == self.SEND_NOTIFICATION:
                await self.broadcast_to_group(
                    self.lobby_name,
                    'notification',
                    {
                        'client_id': self.client_id,
                        'message': data['message'],
                    }
                )
            elif command == self.SERVER_TIME:
                await self.send_info_to_client(self.SERVER_TIME, timezone.now().isoformat())
            elif command == self.CREATE_USER:
                result = await self.create_user(data['user_data'])
                await self.send_info_to_client(self.CREATE_USER, result)
            elif command == self.MODIFY_USER:
                result = await self.modify_user(self.client_id, data['changes'])
                await self.send_info_to_client(self.MODIFY_USER, result)
            elif command == self.INVITE_TO_MATCH:
                await self.invite_to_match(data['client_id'], data['match_id'])
            elif command == self.ACCEPT_MATCH:
                await self.accept_match(data['client_id'], data['match_id'])
            elif command == self.REJECT_MATCH:
                await self.reject_match(data['client_id'], data['match_id'])
            elif command == self.CANCEL_MATCH:
                await self.cancel_match(data['client_id'], data['match_id'])
            elif command == self.SEND_FRIEND_REQUEST:
                await self.send_friend_request(data['client_id'])
            elif command == self.ACCEPT_FRIEND_REQUEST:
                await self.accept_friend_request(data['client_id'])
            elif command == self.REJECT_FRIEND_REQUEST:
                await self.reject_friend_request(data['client_id'])
            elif command == self.CANCEL_FRIEND_REQUEST:
                await self.cancel_friend_request(data['client_id'])
            elif command == self.GET_USER_INFO:
                await self.send_info_to_client(self.GET_USER_INFO, await self.get_user_info(data['client_id']))
            elif command == self.INVITE_TO_TOURNAMENT:
                await self.invite_to_tournament(data['client_id'], data['tournament_id'])
            elif command == self.ACCEPT_TOURNAMENT:
                await self.accept_tournament(data['client_id'], data['tournament_id'])
            elif command == self.REJECT_TOURNAMENT:
                await self.reject_tournament(data['client_id'], data['tournament_id'])
            elif command == self.CANCEL_TOURNAMENT:
                await self.cancel_tournament(data['client_id'], data['tournament_id'])
            elif command == self.JOIN_QUEUE:
                await self.join_queue(data['queue_name'], self.client_id)
            elif command == self.LEAVE_QUEUE:
                await self.leave_queue(data['queue_name'], self.client_id)
            elif command == self.CREATE_3v3:
                await self.create_tournament(self.client_id, data['tournament_name'])
            elif command == self.JOIN_3v3:
                await self.join_tournament()
            elif command == self.START_3v3:
                await self.start_tournament()
            elif command == self.NEXT_MATCH:
                await self.get_next_match_or_winner()
            else:
                await self.send_info_to_client(self.CMD_NOT_FOUND, text_data)

        except json.JSONDecodeError as e:
            error_message = f"Error in receive method: {e}"
            print(error_message)
            logging.error(error_message)
        except Exception as e:
            error_message = f"Error in receive method: {e}"
            print(error_message)
            logging.error(error_message)
# ---------------------------------------

# Messaging methods
    async def broadcast(self, event):
        try:
            command = event['command']
            data = event['data']
            
            await self.send(text_data=json.dumps({
                'type': command,
                'data': data
            }))
        except Exception as e:
            error_message = f"Error in broadcast method: {e}"
            print(error_message)
            logging.error(error_message)

    async def broadcast_to_group(self, group_name, command, data):
        try:
            await self.channel_layer.group_send(
                group_name,
                {
                    'type': 'broadcast',
                    'command': command,
                    'data': data
                }
            )
        except Exception as e:
            error_message = f"Error in broadcast_to_group method: {e}"
            print(error_message)
            logging.error(error_message)

    async def message_another_player(self, user_id, command, data):
        try:
            await self.channel_layer.group_send(
                user_id,
                {
                    'type': 'broadcast',
                    'command': command,
                    'data': data
                }
            )
        except Exception as e:
            error_message = f"Error in message_another_player method: {e}"
            print(error_message)
            logging.error(error_message)

    async def send_info_to_client(self, command, data):
        try:
            print(f'Sending message to client {self.client_id} with data: {data}')
            await self.send(text_data=json.dumps({
                'type': command,
                'data': data
            }))
        except Exception as e:
            error_message = f"Error in send_info_to_client method: {e}"
            print(error_message)
            logging.error(error_message)
# ---------------------------------------

# Predefined Arrival Departure methods
    async def announce_arrival(self):
        try:
            await self.broadcast_to_group(
                self.lobby_name,
                'user_joined',
                {
                    'client_id': self.client_id,
                    'lobby_name': self.lobby_name,
                    'online_users': self.list_of_online_users,
                }
            )
        except Exception as e:
            error_message = f"Error in announce_arrival method: {e}"
            print(error_message)
            logging.error(error_message)
            await self.disconnect(1000)

    async def announce_departure(self):
        try:
            await self.broadcast_to_group(
                self.lobby_name,
                'user_left',
                {
                    'client_id': self.client_id,
                    'lobby_name': self.lobby_name,
                    'online_users': self.list_of_online_users,
                }
            )
        except Exception as e:
            error_message = f"Error in announce_departure method: {e}"
            print(error_message)
            logging.error(error_message)
            await self.disconnect(1000)
# ---------------------------------------

# Predefined Matchmaking methods
    async def invite_to_match(self, user_id, match_id):
        try:
            message_for_client = await self.modify_user(self.client_id, {'add_sent_invites': user_id, 'invite_type': 'match'})
            message_other_client = await self.modify_user(user_id, {'add_received_invites': self.client_id, 'invite_type': 'match'})

            await self.message_another_player(
                user_id,
                'recieved_match_invite',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': self.client_id,
                    'match_id': match_id,
                    'message': message_other_client,
                }
            )
            await self.send_info_to_client(
                'sent_match_invite',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': user_id,
                    'message': message_for_client,
                    
                }
            )
        except Exception as e:
            print(f'Exception in invite_to_game {e}')
            await self.disconnect(1000)

    async def accept_match(self, user_id, match_id):
        try:

            message_for_client = await self.modify_user(self.client_id, {'remove_recieved_invites': user_id, 'invite_type': 'match'})
            message_other_client = await self.modify_user(user_id, {'remove_sent_invites': self.client_id, 'invite_type': 'match'})

            await self.message_another_player(
                user_id,
                'match_accepted',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': self.client_id,
                    'match_id': match_id,
                    'message': message_other_client,
                }
            )
            await self.send_info_to_client(
                'accept_match',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': user_id,
                    'match_id': match_id,
                    'message': message_for_client,
                }
            )
        except Exception as e:
            print(f'Exception in accept_match {e}')
            await self.disconnect(1000)

    async def reject_match(self, user_id, match_id):
        try:
            message_for_client = await self.modify_user(self.client_id, {'remove_recieved_invites': user_id, 'invite_type': 'match'})
            message_other_client = await self.modify_user(user_id, {'remove_sent_invites': self.client_id, 'invite_type': 'match'})

            await self.message_another_player(
                user_id,
                'match_rejected',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': self.client_id,
                    'match_id': match_id,
                    'message': message_other_client,
                }
            )
            await self.send_info_to_client(
                'reject_match',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': user_id,
                    'match_id': match_id,
                    'message': message_for_client,
                }
            )
        except Exception as e:
            print(f'Exception in reject_match {e}')
            await self.disconnect(1000)

    async def cancel_match(self, user_id, match_id):
        try:
            message_for_client = await self.modify_user(self.client_id, {'remove_sent_invites': user_id, 'invite_type': 'match'})
            message_other_client = await self.modify_user(user_id, {'remove_recieved_invites': self.client_id, 'invite_type': 'match'})

            await self.message_another_player(
                user_id,
                'match_cancelled',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': self.client_id,
                    'match_id': match_id,
                    'message': message_other_client,
                }
            )
            await self.send_info_to_client(
                'cancel_match',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': user_id,
                    'match_id': match_id,
                    'message': message_for_client,
                }
            )
        except Exception as e:
            print(f'Exception in cancel_match {e}')
            await self.disconnect(1000)
# ---------------------------------------

# Predefined Friend methods
    async def send_friend_request(self, user_id):
        try:
            message_for_client = await self.modify_user(self.client_id, {'add_sent_invites': user_id, 'invite_type': 'friend_request'})
            message_other_client = await self.modify_user(user_id, {'add_received_invites': self.client_id, 'invite_type': 'friend_request'})

            await self.message_another_player(
                user_id,
                'recieved_friend_request',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': self.client_id,
                    'message': message_other_client,
                }
            )
            # Advice the user that the friend request was sent
            await self.send_info_to_client(
                'sent_friend_request',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': user_id,
                    'message': message_for_client,
                }
            )

        except Exception as e:
            print(f'Exception in send_friend_request {e}')
            await self.disconnect(1000)

    @database_sync_to_async
    def check_if_friend_request_exists(self, user_id):
        from api.userauth.models import CustomUser
        try:
            user = CustomUser.objects.get(pk=int(self.client_id))
        except Exception:
            return False
        
        friend_requests = user.list_of_received_invites
        ids = [int(req.get('invite_id')) for req in friend_requests]
        return int(user_id) in ids
        

    async def accept_friend_request(self, user_id):
        try:
            # Add the current user as a friend for the other person

            if not await self.check_if_friend_request_exists(user_id):
                print("No such friend request")
                return
            
            message = await self.add_friendship(pk=user_id)
            print(message)

            # Remove the friend request from both users lists
            message_to_client = await self.modify_user(self.client_id, {'remove_recieved_invites': user_id, 'invite_type': 'friend_request'})
            message_other_client = await self.modify_user(user_id, {'remove_sent_invites': self.client_id, 'invite_type': 'friend_request'})

            # Send a message to the other person
            await self.message_another_player(
                user_id,
                'friend_request_accepted',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': self.client_id,
                    'message': message_other_client,
                }
            )
            # Send a message to the current user
            await self.send_info_to_client(
                'accept_friend_request',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': user_id,
                    'message': message_to_client,
                }
            )

        except Exception as e:
            print(f'Exception in accept_friend_request: {e}')
            await self.disconnect(1000)

    async def reject_friend_request(self, user_id):
        try:

            message_to_client = await self.modify_user(self.client_id, {'remove_recieved_invites': user_id, 'invite_type': 'friend_request'})
            message_other_client = await self.modify_user(user_id, {'remove_sent_invites': self.client_id, 'invite_type': 'friend_request'})

            await self.message_another_player(
                user_id,
                'friend_request_rejected',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': self.client_id,
                    'message': message_other_client,
                }
            )
            await self.send_info_to_client(
                'reject_friend_request',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': user_id,
                    'message': message_to_client,
                }
            )
        except Exception as e:
            print(f'Exception in reject_friend_request {e}')
            await self.disconnect(1000)

    async def cancel_friend_request(self, user_id):
        try:
            message_for_client = await self.modify_user(self.client_id, {'remove_sent_invites': user_id, 'invite_type': 'friend_request'})
            message_other_client = await self.modify_user(user_id, {'remove_recieved_invites': self.client_id, 'invite_type': 'friend_request'})

            await self.message_another_player(
                user_id,
                'friend_request_cancelled',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': self.client_id,
                    'message': message_other_client,
                }
            )
            await self.send_info_to_client(
                'cancel_friend_request',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': user_id,
                    'message': message_for_client,
                }
            )
        except Exception as e:
            print(f'Exception in cancel_friend_request {e}')
            await self.disconnect(1000)
# ---------------------------------------

# Predefined Tournament methods
    async def invite_to_tournament(self, user_id, tournament_id):
        try:

            message_for_client = await self.modify_user(self.client_id, {'add_sent_invites': user_id, 'invite_type': 'tournament'})
            message_other_client = await self.modify_user(user_id, {'add_received_invites': self.client_id, 'invite_type': 'tournament'})

            await self.message_another_player(
                user_id,
                'recieved_tournament_invite',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': self.client_id,
                    'tournament_id': tournament_id,
                    'message': message_other_client,
                }
            )
            await self.send_info_to_client(
                'sent_tournament_invite',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': user_id,
                    'tournament_id': tournament_id,
                    'message': message_for_client,
                }
            )
        except Exception as e:
            print(f'Exception in invite_to_tournament {e}')
            await self.disconnect(1000)

    async def accept_tournament(self, user_id, tournament_id):
        try:

            message_for_client = await self.modify_user(self.client_id, {'remove_recieved_invites': user_id, 'invite_type': 'tournament'})
            message_other_client = await self.modify_user(user_id, {'remove_sent_invites': self.client_id, 'invite_type': 'tournament'})

            await self.message_another_player(
                user_id,
                'tournament_accepted',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': self.client_id,
                    'tournament_id': tournament_id,
                    'message': message_other_client,
                }
            )
            await self.send_info_to_client(
                'accept_tournament',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': user_id,
                    'tournament_id': tournament_id,
                    'message': message_for_client,

                }
            )

        except Exception as e:
            print(f'Exception in accept_tournament {e}')
            await self.disconnect(1000)

    async def reject_tournament(self, user_id, tournament_id):
        try:

            message_for_client = await self.modify_user(self.client_id, {'remove_recieved_invites': user_id, 'invite_type': 'tournament'})
            message_other_client = await self.modify_user(user_id, {'remove_sent_invites': self.client_id, 'invite_type': 'tournament'})

            await self.message_another_player(
                user_id,
                'tournament_rejected',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': self.client_id,
                    'tournament_id': tournament_id,
                    'message': message_other_client,
                }
            )
            await self.send_info_to_client(
                'reject_tournament',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': user_id,
                    'tournament_id': tournament_id,
                    'message': message_for_client,
                }
            )
        except Exception as e:
            print(f'Exception in reject_tournament {e}')
            await self.disconnect(1000)

    async def cancel_tournament(self, user_id, tournament_id):
        try:

            message_for_client = await self.modify_user(self.client_id, {'remove_sent_invites': user_id, 'invite_type': 'tournament'})
            message_other_client = await self.modify_user(user_id, {'remove_recieved_invites': self.client_id, 'invite_type': 'tournament'})

            await self.message_another_player(
                user_id,
                'tournament_cancelled',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': self.client_id,
                    'tournament_id': tournament_id,
                    'message': message_other_client,
                }
            )
            await self.send_info_to_client(
                'cancel_tournament',
                {
                    'time': timezone.now().isoformat(),
                    'client_id': user_id,
                    'tournament_id': tournament_id,
                    'message': message_for_client,
                }
            )
        except Exception as e:
            print(f'Exception in cancel_tournament {e}')
            await self.disconnect(1000)
# ---------------------------------------

# Object existence methods
    @database_sync_to_async
    def does_not_exist(self, pk):
        try:
            User = import_string('api.userauth.models.CustomUser')
            user = get_object_or_404(User, pk=pk)
            # Check if the user is already connected on another client
            # if self.list_of_online_users.get(self.client_id):
            #     return True

            self.list_of_online_users[self.client_id] = user.username
            if user.is_superuser:
                self.list_of_admins[self.client_id] = user.username
            return False

        except Http404:
            return True

        except Exception as e:
            print(e)
            self.disconnect(1000)
# ---------------------------------------

# Client modification methods
    @database_sync_to_async
    def modify_user(self, pk, changes):
        try:
            User = import_string('api.userauth.models.CustomUser')
            user = get_object_or_404(User, pk=pk)

            if user is None:
                return {
                    'status': 'error',
                    'message': 'User not found',
                }

            if changes.get('add_sent_invites'):
                self.add_sent_invites(user, changes)
                return {
                    'status': 'ok',
                    'message': 'Sent invite added successfully',
                }
            
            if changes.get('remove_sent_invites'):
                self.remove_sent_invites(user, changes)
                return {
                    'status': 'ok',
                    'message': 'Sent invite removed successfully',
                }
            
            if changes.get('add_received_invites'):
                self.add_received_invites(user, changes)
                return {
                    'status': 'ok',
                    'message': 'Recieved invite added successfully',
                }

            if changes.get('remove_recieved_invites'):
                self.remove_received_invites(user, changes)
                return {
                    'status': 'ok',
                    'message': 'Recieved invite removed successfully',
                }

            for key, value in changes.items():
                setattr(user, key, value)

            user.save()

            return {
                'status': 'ok',
                'message': 'User modified successfully',
            }

        except Exception as e:
            print(e)
            print(f'Could not find user with id {pk}')
            return None
# ---------------------------------------

# Invites list methods (Sent and Received)
    def add_received_invites(self, user, change):
        try:
            invite_id = change['add_received_invites']
            invite_type = change['invite_type']
            user.add_received_invites(invite_id, invite_type)

        except Exception as e:
            print(e)

    def remove_received_invites(self, user, change):
        try:
            invite_id = change['remove_recieved_invites']
            invite_type = change['invite_type']
            user.remove_received_invites(invite_id, invite_type)

        except Exception as e:
            print(e)

    def add_sent_invites(self, user, change):
        try:
            invite_id = change['add_sent_invites']
            invite_type = change['invite_type']
            user.add_sent_invites(invite_id, invite_type)

        except Exception as e:
            print(e)

    def remove_sent_invites(self, user, change):
        try:
            invite_id = change['remove_sent_invites']
            invite_type = change['invite_type']
            user.remove_sent_invites(invite_id, invite_type)

        except Exception as e:
            print(e)
# ---------------------------------------

# Database methods synchronised with the channel layer
    @database_sync_to_async
    @transaction.atomic
    def add_friendship(self, pk):
        try:
            Friendship = import_string('api.userauth.models.Friendship')
            User = import_string('api.userauth.models.CustomUser')

            user = get_object_or_404(User, id=self.client_id)

            if Friendship.objects.filter(user=user).exists():
                user_friend = Friendship.objects.get(user=user)
            else:
                user_friend = Friendship.objects.create(user=user)

            friend = get_object_or_404(User, id=pk)

            if user == friend:
                return f'You cannot add yourself as a friend'

            if friend in user_friend.friends.all():
                return f'{friend.username} is already your friend'
            
            # Check if the intended friend has a Friendship object, create one if not
            if Friendship.objects.filter(user=friend).exists():
                friend_friend = Friendship.objects.get(user=friend)
            else:
                friend_friend = Friendship.objects.create(user=friend)

            # Check if the intended friend has blocked the current user
            if user in friend_friend.blocked_users.all():
                return f'{friend.username} has blocked you'
            # Add friend for the current user
            user_friend.friends.add(friend)
            user_friend.save()

            # Add the current user as a friend for the other user
            friend_friend.friends.add(user)
            friend_friend.save()

            return f'{friend.username} added as a friend'

        except Exception as e:
            print(e)    
        
    @database_sync_to_async
    def create_user(self, user_data):
        try:
            User = import_string('api.userauth.models.CustomUser')

            # Extract the username and password fields
            username = user_data['username']
            password = user_data['password']

            # Use create to create a new user with mandatory fields
            user = User.objects.create(
                username=username,
                password=password,
            )

            # Update optional fields if provided
            if 'email' in user_data:
                user.email = user_data['email']

            if 'first_name' in user_data:
                user.first_name = user_data['first_name']

            if 'last_name' in user_data:
                user.last_name = user_data['last_name']

            user.is_active = True
            user.is_staff = False
            user.is_superuser = False

            user.save()

            return {
                'status': 'ok',
                'message': 'User created successfully',
            }

        except Exception as e:
            print(f'Error creating user: {e}')
            return None

    @database_sync_to_async
    def get_user_info(self, pk):
        try:
            User = import_string('api.userauth.models.CustomUser')
            print(f'Getting info for user {pk} type {type(pk)}')
            print(f'The requesting user is {self.client_id} type {type(self.client_id)}')
            
            user = get_object_or_404(User, pk=pk)
            self_user = get_object_or_404(User, pk=self.client_id)

            print(f'Getting info for user {user.username} with its pk {pk} with type {type(pk)}')
            print(f'The requesting user is {self_user.username} with its pk {self.client_id} with type {type(self.client_id)}')
         
            if self_user.is_superuser:
                return {
                    'status': 'ok',
                    'message': 'User info retrieved successfully',
                    'data': {
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_active': user.is_active,
                        'is_staff': user.is_staff,
                        'is_superuser': user.is_superuser,
                        'pending_invites': user.get_pending_invites(),
                    }
                }

            return {
                'status': 'ok',
                'message': 'User info retrieved successfully',
                'data': {
                    'username': user.username,
                    'is_active': user.is_active,
                    'pending_invites': user.get_pending_invites(),
                }
            }

        except Exception as e:
            print(e)
            print(f'Could not find user with id {self.client_id}')
            return None

    @database_sync_to_async
    def get_sent_invites(self, pk):
        try:
            User = import_string('api.userauth.models.CustomUser')
            user = get_object_or_404(User, pk=pk)
            return user.get_sent_invites()

        except Exception as e:
            print(e)
            print(f'Could not find user with id {pk}')
            return None
        
    @database_sync_to_async 
    def get_recieved_invites(self, pk):
        try:
            User = import_string('api.userauth.models.CustomUser')
            user = get_object_or_404(User, pk=pk)
            return user.get_received_invites()

        except Exception as e:
            print(e)
            print(f'Could not find user with id {pk}')
            return None

    @database_sync_to_async
    def create_match(self, user_id, opponent_id):
        try:
            Match = import_string('api.tournament.models.Match')
            User = import_string('api.userauth.models.CustomUser')
            user = get_object_or_404(User, pk=user_id)
            opponent = get_object_or_404(User, pk=opponent_id)
            match = Match.objects.create(
                player1=user,
                player2=opponent,
                active=True
            )
            match.save()
            return match.id
        except Exception as e:
            print(f'Exception in create_match {e}')
            return None

# Multiplayer Tournament methods
    async def start_tournament(self):
        try:
            BestofThree = import_string('api.best_of_three.models.BestofThree')
            Match = import_string('api.tournament.models.Match')
            User = import_string('api.userauth.models.CustomUser')

            if not LobbyConsumer.tournament.get(self.client_id):
                await self.send_info_to_client(
                    'no_tournament',
                    {
                        "message": "You are not in a tournament"
                    }
                )
                return None

            print(LobbyConsumer.tournament[self.client_id])

            if int(self.client_id) != LobbyConsumer.tournament[self.client_id]["admin"]:
                await self.send_info_to_client(
                    'not_admin',
                    {
                        "message": "You are not the admin"
                    }
                )
                return None

            print(LobbyConsumer.tournament[self.client_id]["players"])

            players_ids = LobbyConsumer.tournament[self.client_id]["players"]
            players = await database_sync_to_async(User.objects.filter)(id__in=players_ids)

            if len(players) < 2:
                await self.send_info_to_client(
                    'not_enough_players',
                    {
                        "message": "There are not enough players"
                    }
                )
                return None

            print(f'Players: {players}')

            # Shuffle the players to create random pairs
            random.shuffle(players)
            num_matches = len(players) // 2

            matches = []

            for i in range(num_matches):
                match = await database_sync_to_async(Match.objects.create)(
                    player1=players[i * 2],
                    player2=players[i * 2 + 1],
                    active=True,
                    best_of_three_id=int(LobbyConsumer.tournament[self.client_id]["id"])
                )
                await database_sync_to_async(match.save)()
                matches.append(match)
                print(f'Match {match.id} - Player 1: {match.player1} Player 2: {match.player2}')

            await self.send_info_to_client(
                'tournament_started',
                {
                    "message": "The tournament has started",
                    "data": {
                        "tournament_name": LobbyConsumer.tournament[self.client_id]["name"],
                        "tournament_id": LobbyConsumer.tournament[self.client_id]["id"],
                        "matches": [match.id for match in matches],
                    }
                }
            )

            for player in players:
                await self.message_another_player(
                    str(player.id),
                    'tournament_started',
                    {
                        "message": "The tournament has started",
                        "data": {
                            "tournament_name": LobbyConsumer.tournament[self.client_id]["name"],
                            "tournament_id": LobbyConsumer.tournament[self.client_id]["id"],
                            "matches": [match.id for match in matches],
                        }
                    }
                )

            # Update BestofThree object with match information
            tournament = await database_sync_to_async(get_object_or_404)(BestofThree, pk=LobbyConsumer.tournament[self.client_id]["id"])
            tournament.matches.set(matches)

            # Clear tournament information from the list
            # del LobbyConsumer.tournament[self.client_id]

            return None

        except Exception as e:
            print(f'Exception in start_tournament {e}')
            return None

    async def join_tournament(self):
        try:
            BestofThree = import_string('api.best_of_three.models.BestofThree')
            User = import_string('api.userauth.models.CustomUser')

            if LobbyConsumer.tournament.get(self.client_id):
                await self.send_info_to_client(
                    'already_in_tournament',
                    {
                        "message": "You are already in a tournament"
                    }
                )
                return None

            for tournament_name, tournament in LobbyConsumer.tournament.items():
                if tournament["open"]:
                    LobbyConsumer.tournament[tournament_name]["players"].append(int(self.client_id))
                    print(LobbyConsumer.tournament[tournament_name])

                    await self.send_info_to_client(
                        'joined_tournament',
                        {
                            "message": "You have joined the tournament",
                            "data": {
                                "tournament_name": tournament_name,
                                "tournament_id": tournament["id"],
                                "admin": str(tournament["admin"]),
                            }
                        }
                    )

                    # Send message to admin that someone joined and the tournament is ready to start
                    await self.message_another_player(
                        str(tournament["admin"]),
                        'tournament_ready',
                        {
                            "message": "Someone joined the tournament",
                            "data": {
                                "tournament_name": tournament_name,
                                "tournament_id": tournament["id"],
                                "opponent": self.client_id,
                            }
                        }
                    )

                    LobbyConsumer.tournament[tournament_name]["open"] = False

                    # Add the joining player to the BestofThree object
                    user = await database_sync_to_async(get_object_or_404)(User, pk=int(self.client_id))
                    tournament_obj = await database_sync_to_async(get_object_or_404)(BestofThree, pk=tournament["id"])
                    tournament_obj.players.add(user)
                    await database_sync_to_async(tournament_obj.save)()
                    print(LobbyConsumer.tournament[tournament_name])

                    return

                else:
                    await self.send_info_to_client(
                        'no_tournaments_available',
                        {
                            "message": "There are no tournaments available"
                        }
                    )
                    return

        except Exception as e:
            print(f'Exception in join_tournament {e}')
            return None

    async def create_tournament(self, user_id, tournament_name):
        print("Creating tournament")
        try:
            BestofThree = import_string('api.best_of_three.models.BestofThree')
            User = import_string('api.userauth.models.CustomUser')

            user = await database_sync_to_async(get_object_or_404)(User, pk=user_id)

            if not tournament_name:
                await self.send_info_to_client(
                    'tournament_name_missing',
                    {
                        "message": "Tournament name is missing"
                    }
                )
                return None

            if LobbyConsumer.tournament.get(self.client_id):
                await self.send_info_to_client(
                    'tournament_exists',
                    {
                        "message": "You are already in a tournament"
                    }
                )
                return None

            # Check if the user is already in another tournament
            for tournament_name, tournament in LobbyConsumer.tournament.items():
                if int(self.client_id) in tournament["players"]:
                    await self.send_info_to_client(
                        'already_in_tournament',
                        {
                            "message": "You are already in a tournament"
                        }
                    )
                    return None

            tournament_obj = await database_sync_to_async(BestofThree.objects.create)(
                name=tournament_name,
                admin=user,
                winner=None,
                date_played=None,
                active=True
            )

            LobbyConsumer.tournament[self.client_id] = {
                "id": tournament_obj.id,
                "name": tournament_obj.name,
                "admin": int(self.client_id),
                "players": [int(self.client_id)],
                "open": True
            }

            await database_sync_to_async(tournament_obj.save)()

            print(LobbyConsumer.tournament[self.client_id])
            print(LobbyConsumer.tournament)

            await self.send_info_to_client(
                'tournament_created',
                {
                    "message": "Tournament created",
                    "data": {
                        "tournament_name": tournament_obj.name,
                        "tournament_id": tournament_obj.id
                    }
                }
            )

            return tournament_obj.id

        except Exception as e:
            print(f'Exception in create_tournament {e}')
            return None

    async def get_next_round_or_winner(self):
        try:
            BestofThree = import_string('api.best_of_three.models.BestofThree')
            Match = import_string('api.tournament.models.Match')

            if not LobbyConsumer.tournament.get(self.client_id):
                await self.send_info_to_client('no_tournament', {"message": "You are not in a tournament"})
                return None

            print("Getting tournament...")
            tournament_id = LobbyConsumer.tournament[self.client_id]["id"]
            tournament = await database_sync_to_async(get_object_or_404)(BestofThree, pk=tournament_id)

            get_match = database_sync_to_async(get_object_or_404)
            print("Getting matches...")
            matches = await database_sync_to_async(Match.objects.filter)(best_of_three=tournament)

            print("Checking if all matches are not active...")
            if all(not match.active for match in matches):
                # All matches are not active
                if tournament.is_finished():
                    # Tournament is finished, determine the winner
                    winner = await database_sync_to_async(lambda: tournament.winner)()
                    if winner:
                        await self.send_info_to_client(
                            'tournament_winner',
                            {
                                "message": "Tournament winner",
                                "data": {
                                    "winner": winner.id,
                                }
                            }
                        )
                    else:
                        await self.send_info_to_client('no_winner', {"message": "There is no winner"})
                else:
                    # Start the next round
                    await self.start_next_round(tournament)
            else:
                # Some matches are still active
                await self.send_info_to_client('matches_active', {"message": "Some matches are still active"})

        except Exception as e:
            print(f'Exception in get_next_round_or_winner {e}')
            return None

    async def start_next_round(self, tournament):
        try:
            Match = import_string('api.tournament.models.Match')
            User = import_string('api.userauth.models.CustomUser')

            players = await database_sync_to_async(tournament.players.all)()

            if len(players) % 2 != 0:
                # Handle odd number of players if needed
                # Possibly add a bye to a random player
                pass

            # Shuffle the players to create random pairs
            random.shuffle(players)
            num_matches = len(players) // 2

            matches = []

            for i in range(num_matches):
                match = await database_sync_to_async(Match.objects.create)(
                    player1=players[i * 2],
                    player2=players[i * 2 + 1],
                    active=True,
                    best_of_three=tournament
                )
                await database_sync_to_async(match.save)()
                matches.append(match)
                print(f'Match {match.id} - Player 1: {match.player1} Player 2: {match.player2}')

            tournament.matches.set(matches)

            await self.send_info_to_client(
                'next_round_started',
                {
                    "message": "The next round has started",
                    "data": {
                        "tournament_name": tournament.name,
                        "tournament_id": tournament.id,
                        "matches": [match.id for match in matches],
                    }
                }
            )

            for player in players:
                await self.message_another_player(
                    str(player.id),
                    'next_round_started',
                    {
                        "message": "The next round has started",
                        "data": {
                            "tournament_name": tournament.name,
                            "tournament_id": tournament.id,
                            "matches": [match.id for match in matches],
                        }
                    }
                )

        except Exception as e:
            print(f'Exception in start_next_round {e}')
            return None
# ---------------------------------------


# WebSocket close codes

# | Close code (uint16) | Codename               | Internal | Customizable | Description |
# |---------------------|------------------------|----------|--------------|-------------|
# | 0 - 999             |                        | Yes      | No           | Unused |
# | 1000                | `CLOSE_NORMAL`         | No       | No           | Successful operation / regular socket shutdown |
# | 1001                | `CLOSE_GOING_AWAY`     | No       | No           | Client is leaving (browser tab closing) |
# | 1002                | `CLOSE_PROTOCOL_ERROR` | Yes      | No           | Endpoint received a malformed frame |
# | 1003                | `CLOSE_UNSUPPORTED`    | Yes      | No           | Endpoint received an unsupported frame (e.g. binary-only endpoint received text frame) |
# | 1004                |                        | Yes      | No           | Reserved |
# | 1005                | `CLOSED_NO_STATUS`     | Yes      | No           | Expected close status, received none |
# | 1006                | `CLOSE_ABNORMAL`       | Yes      | No           | No close code frame has been receieved |
# | 1007                | *Unsupported payload*  | Yes      | No           | Endpoint received inconsistent message (e.g. malformed UTF-8) |
# | 1008                | *Policy violation*     | No       | No           | Generic code used for situations other than 1003 and 1009 |
# | 1009                | `CLOSE_TOO_LARGE`      | No       | No           | Endpoint won't process large frame |
# | 1010                | *Mandatory extension*  | No       | No           | Client wanted an extension which server did not negotiate |
# | 1011                | *Server error*         | No       | No           | Internal server error while operating |
# | 1012                | *Service restart*      | No       | No           | Server/service is restarting |
# | 1013                | *Try again later*      | No       | No           | Temporary server condition forced blocking client's request |
# | 1014                | *Bad gateway*          | No       | No           | Server acting as gateway received an invalid response |
# | 1015                | *TLS handshake fail*   | Yes      | No           | Transport Layer Security handshake failure |
# | 1016 - 1999         |                        | Yes      | No           | Reserved for later |
# | 2000 - 2999         |                        | Yes      | Yes          | Reserved for websocket extensions |
# | 3000 - 3999         |                        | No       | Yes          | Registered first come first serve at IANA |
# | 4000 - 4999         |                        | No       | Yes          | Available for applications |