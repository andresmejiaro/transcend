import json
from channels.generic.websocket import AsyncWebsocketConsumer
from ws_api.python_pong.Player import Player
from ws_api.python_pong.Game import Game
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.utils import timezone
from django.db import transaction


from django.utils.module_loading import import_string

class LobbyConsumer(AsyncWebsocketConsumer):

    list_of_admins = {}
    list_of_online_users = {}
    lobby_name = 'lobby'

# Define constants for commands
    LIST_OF_USERS = 'list_of_users'                     # Command to send the list of online users
    SEND_PRV_MSG = 'send_prv_msg'                       # Command to send a private message
    SEND_NOTIFICATION = 'send_notification'             # Command to send a notification
    CMD_NOT_FOUND = 'command_not_found'                 # Command to send when a command is not found
    CLOSE_CONNECTION = 'close_connection'               # Command to close the connection
    CREATE_USER = 'create_user'                         # Command to create a user arguments: pass the values as of 'user_data'
    MODIFY_USER = 'modify_user'                         # Command to modify a user arguments: pass the values as of 'changes'
    SERVER_TIME = 'server_time'                         # Command to send the server time
    INVITE_TO_MATCH = 'invite_to_match'                 # Command to invite a user to a match arguments: pass the values as of 'client_id' and 'match_id'
    ACCEPT_MATCH = 'accept_match'                       # Command to accept a match arguments: pass the values as of 'client_id' and 'match_id'
    REJECT_MATCH = 'reject_match'                       # Command to reject a match arguments: pass the values as of 'client_id' and 'match_id'
    CANCEL_MATCH = 'cancel_match'                       # Command to cancel a match arguments: pass the values as of 'client_id' and 'match_id'
    SEND_FRIEND_REQUEST = 'send_friend_request'         # Command to send a friend request arguments: pass the values as of 'client_id'
    ACCEPT_FRIEND_REQUEST = 'accept_friend_request'     # Command to accept a friend request arguments: pass the values as of 'client_id'   
    REJECT_FRIEND_REQUEST = 'reject_friend_request'     # Command to reject a friend request arguments: pass the values as of 'client_id'
    CANCEL_FRIEND_REQUEST = 'cancel_friend_request'     # Command to cancel a friend request arguments: pass the values as of 'client_id'
    GET_USER_INFO = 'get_user_info'                     # Command to get user info arguments: pass the values as of 'client_id'


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = None
        self.client_username = None

# Channel methods (Connect, Disconnect, Receive)
    async def connect(self):
        try:
            query_string = self.scope['query_string'].decode('utf-8')
            query_params = parse_qs(query_string)
            self.client_id = query_params['client_id'][0]

            # Get the user and see if they exist before accepting the connection
            if await self.does_not_exist(self.client_id):
                await self.close()
                return

            await self.accept()

            await self.channel_layer.group_add(self.lobby_name, self.channel_name)
            await self.channel_layer.group_add(self.client_id, self.channel_name)

            await self.announce_arrival()


        except Exception as e:
            print(f"Error in connect method: {e}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            print(f'Client {self.client_id} disconnected with code {close_code}')
            if self.list_of_online_users.get(self.client_id):
                del self.list_of_online_users[self.client_id]
                        # Remove client from the group channel
            await self.channel_layer.group_discard(self.lobby_name, self.channel_name)
            await self.channel_layer.group_discard(self.client_id, self.channel_name)

            # Send info of group status every time a client leaves
            await self.announce_departure()
            self.close()

        except Exception as e:
            print(f"Error in disconnect method: {e}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            command = data.get('command')
            data = data.get('data')

            if command == self.LIST_OF_USERS:
                await self.send_info_to_client(self.LIST_OF_USERS, self.list_of_online_users)
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
                await self.send_info_to_client(self.GET_USER_INFO, await self.get_user_info())

            else:
                await self.send_info_to_client(self.CMD_NOT_FOUND, text_data)

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON data: {e}")
        except Exception as e:
            print(f"Error in receive method: {e}")
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
            print(f'Error in broadcast method: {e}')

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
            print(f'Error in broadcast_to_group method: {e}')

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
            print(f'Error in message_another_player method: {e}')

    async def send_info_to_client(self, command, data):
        try:
            print(f'Sending message to client {self.client_id} with data: {data}')
            await self.send(text_data=json.dumps({
                'type': command,
                'data': data
            }))
        except Exception as e:
            print(f'Error in send_info_to_client method: {e}')
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
            print(f'Exception in announce_arrival {e}')
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
            print(f'Exception in announce_departure {e}')
            await self.disconnect(1000)

# Predefined Matchmaking methods
    async def invite_to_match(self, user_id, match_id):
        try:
            await self.message_another_player(
                user_id,
                'invite_to_match',
                {
                    'client_id': self.client_id,
                    'match_id': match_id,
                }
            )
        except Exception as e:
            print(f'Exception in invite_to_game {e}')
            await self.disconnect(1000)

    async def accept_match(self, user_id, match_id):
        try:
            await self.message_another_player(
                user_id,
                'accept_match',
                {
                    'client_id': self.client_id,
                    'match_id': match_id,
                }
            )
        except Exception as e:
            print(f'Exception in accept_match {e}')
            await self.disconnect(1000)

    async def reject_match(self, user_id, match_id):
        try:
            await self.message_another_player(
                user_id,
                'reject_match',
                {
                    'client_id': self.client_id,
                    'match_id': match_id,
                }
            )
        except Exception as e:
            print(f'Exception in reject_match {e}')
            await self.disconnect(1000)

    async def cancel_match(self, user_id, match_id):
        try:
            await self.message_another_player(
                user_id,
                'cancel_match',
                {
                    'client_id': self.client_id,
                    'match_id': match_id,
                }
            )
        except Exception as e:
            print(f'Exception in cancel_match {e}')
            await self.disconnect(1000)
# ---------------------------------------

# Predefined Friend methods
    async def send_friend_request(self, user_id):
        try:
            await self.message_another_player(
                user_id,
                'friend_request',
                {
                    'client_id': self.client_id,
                }
            )
        except Exception as e:
            print(f'Exception in send_friend_request {e}')
            await self.disconnect(1000)

    # Predefined Friend methods
    async def accept_friend_request(self, user_id):
        try:
            # Add the current user as a friend for the other person
            message = await self.add_friendship(pk=user_id)

            # Send a message to the other person
            await self.message_another_player(
                user_id,
                'accept_friend_request',
                {
                    'client_id': self.client_id,
                    'message': message,
                }
            )

        except Exception as e:
            print(f'Exception in accept_friend_request: {e}')
            await self.disconnect(1000)

    async def reject_friend_request(self, user_id):
        try:
            await self.message_another_player(
                user_id,
                'reject_friend_request',
                {
                    'client_id': self.client_id,
                }
            )
        except Exception as e:
            print(f'Exception in reject_friend_request {e}')
            await self.disconnect(1000)

    async def cancel_friend_request(self, user_id):
        try:
            await self.message_another_player(
                user_id,
                'cancel_friend_request',
                {
                    'client_id': self.client_id,
                }
            )
        except Exception as e:
            print(f'Exception in cancel_friend_request {e}')
            await self.disconnect(1000)

# ---------------------------------------

# Database methods
    @database_sync_to_async
    def does_not_exist(self, pk):
        try:
            User = import_string('api.userauth.models.CustomUser')
            user = get_object_or_404(User, pk=pk)
            self.list_of_online_users[self.client_id] = user.username
            if user.is_superuser:
                self.list_of_admins[self.client_id] = user.username
            return False

        except Http404:
            return True

        except Exception as e:
            print(e)
            self.disconnect(1000)

    @database_sync_to_async
    def modify_user(self, pk, changes):
        try:
            User = import_string('api.userauth.models.CustomUser')
            user = get_object_or_404(User, pk=pk)

            if user is None:
                print(f'Could not find user with id {pk}')
                return None

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

    @database_sync_to_async
    @transaction.atomic
    def add_friendship(self, pk):
        try:
            Friendship = import_string('api.friends.models.Friendship')
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
    def get_user_info(self):
        try:
            User = import_string('api.userauth.models.CustomUser')
            user = get_object_or_404(User, pk=self.client_id)
            self_user = get_object_or_404(User, pk=self.client_id)

            if user or self_user is None:
                print(f'Could not find user with id {self.client_id}')
                return None
            
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
                    }
                }

            return {
                'status': 'ok',
                'message': 'User info retrieved successfully',
                'data': {
                    'username': user.username,
                    'is_active': user.is_active,
                }
            }

        except Exception as e:
            print(e)
            print(f'Could not find user with id {self.client_id}')
            return None
# ---------------------------------------
