import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from .lobbyutils import LobbyCommands, LobbyFunctions
import asyncio

class Group(object):
    def __init__(self, group_name, lobby_consumer):
        self.lobby_consumer = lobby_consumer
        # String name of the group
        self.group_name = group_name
        # Dictionary of user_id: channel_name (channel_name is the channel name of the user's websocket connection)
        self.users = {}

    async def add_member(self, user_id, channel_name):
        print(f"In class Group, adding user_id: {user_id} with channel_name: {channel_name}")

        if user_id in self.users:
            print(f"User {user_id} already in group {self.group_name}")
            return
        else:
            print(f"User {user_id} with channel_name: {channel_name} added to group {self.group_name}") 

            self.users[user_id] = channel_name
            print(f'self.users: {self.users}')

            await self.lobby_consumer.channel_layer.group_add(
                self.group_name,
                channel_name,
            )

            await self.lobby_consumer.send_info_to_group(
                self.group_name,
                'user_joined',
                {
                    'data': {
                        'message': 'User joined the group',
                        'user_id': user_id,
                        'channel_name': channel_name,
                        'group_name': self.group_name,
                    }
                }
            )

    async def remove_member(self, user_id, channel_name):
        if user_id in self.users:
            # Assuming some asynchronous operation, use "await" if needed
            del self.users[user_id]
            await self.lobby_consumer.channel_layer.group_discard(
                self.group_name,
                channel_name,
            )
            # Announce to everyone in the group that someone has left
            await self.lobby_consumer.send_info_to_group(
                self.group_name,
                'user_left',
                {
                        'data': {
                            'message': 'User left the group',
                            'user_id': user_id,
                            'channel_name': channel_name,
                            'group_name': self.group_name,
                            'group_member_count': self.get_member_count(),
                            'group_members': self.get_channel_all_member_names(),
                            'group_info': self.get_group_info(),
                        }
                }
            ) 
        else:
            print(f"User {user_id} not found in group {self.group_name}")

    async def change_group_name(self, group_name):
        self.group_name = group_name
        # Announce the group name change to everyone in the group
        await self.lobby_consumer.send_info_to_group(
            self.group_name,
            'group_name_changed',
            {
                'data': {
                    'message': 'Group name changed',
                    'group_name': self.group_name,
                }
            }
        )

    async def broadcast(self, command, data):
        """
        Broadcast a message to all members of the group.
        """
        await self.lobby_consumer.send_info_to_group(
            self.group_name,
            command,
            {'data': data}
        )

    def get_member_count(self):
        # Return the number of users in the group
        return len(self.users)

    def get_all_member_ids(self):
        # Return a list of user_ids in the group
        return list(self.users.keys())

    def get_channel_name(self, user_id):
        # Return the channel_name of the user_id
        return self.users.get(user_id)

    def get_channel_all_member_names(self):
        # Return a list of channel_names in the group
        print(f"self.users: {self.users}")
        list_of_member_name = list(self.users.keys())
        return list_of_member_name
        
    def get_group_name(self):
        return self.group_name
    
    def get_group_info(self):
        group_info = {
            'group_name': self.group_name,
            'group_member_count': self.get_member_count(),
            'group_members': self.get_channel_all_member_names(),
        }
        return group_info

    def is_user_in_group(self, user_id):
        # Return True if user is in the group, False otherwise
        return user_id in self.users

    def is_empty(self):
        # Return True if group is empty, False otherwise
        return len(self.users) == 0

class User(object):
    def __init__(self, user_id, channel_name, user_model, lobby_consumer):
        self.lobby_consumer = lobby_consumer
        self.user_id = user_id
        self.channel_name = channel_name
        self.user_model = user_model
        self.groups = []

    def get_user_id(self):
        return self.user_id

    def get_channel_name(self):
        return self.channel_name

    def get_user_model(self):
        return self.user_model

    def get_groups(self):
        return self.groups

    def add_group(self, group):
        self.groups.append(group)

    def remove_group(self, group):
        if group in self.groups:
            self.groups.remove(group)

    def __str__(self):
        return f"{self.user_id}"

class LobbyConsumer(AsyncWebsocketConsumer):
    list_of_groups = {}
    list_of_users = {}
    list_of_channels = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lobbycommands = LobbyCommands(self)
        self.lobbyfunctions = LobbyFunctions(self)
        website_lobby = Group('website_lobby', self)
        if 'website_lobby' not in LobbyConsumer.list_of_groups:
            website_lobby = Group('website_lobby', self)
            LobbyConsumer.list_of_groups['website_lobby'] = website_lobby


    @database_sync_to_async
    def get_user(self, client_id):
        from api.userauth.models import CustomUser as User
        try:
            user = User.objects.get(pk=client_id)
            print(f"User {client_id} found")
            return user
        except User.DoesNotExist:
            print(f"User {client_id} does not exist")
            return

    async def connect(self):
        query_string = self.scope['query_string'].decode('utf-8')
        query_params = parse_qs(query_string)
        self.client_id = query_params.get('client_id', [''])[0]

        print(f"Channel name: {self.channel_name}")

        try:
            self.client_id = int(self.client_id)

            if self.client_id not in LobbyConsumer.list_of_users:
                user_model = await self.get_user(self.client_id)

                if user_model:
                    print(f"User {self.client_id} connected")
                    self.user = User(self.client_id, self.channel_name, user_model, self)
                    website_lobby = LobbyConsumer.list_of_groups['website_lobby']
                    self.user.add_group(website_lobby)
                    # Make a channel layer group for the user
                    user_channel = f'user_{self.client_id}'
                    await self.channel_layer.group_add(
                        user_channel,
                        self.user.get_channel_name(),
                    )

                    # Add the user to the list of users
                    async with asyncio.Lock():
                        LobbyConsumer.list_of_users.update({self.client_id: self.user})
                        LobbyConsumer.list_of_channels[str(self.client_id)] = self.channel_name

                    # Add the user to the website_lobby group
                    await website_lobby.add_member(self.client_id, self.channel_name)
                    await self.accept()
                    self.send(text_data=json.dumps({
                        'type': 'information',
                        'command': 'connected',
                        'data': {
                            'user_id': self.client_id,
                        }
                    }))
                    print(f"User {self.client_id} added to website_lobby with channel_name: {self.channel_name} and user_model: {user_model} with type: {type(user_model)}")

        except ValueError:
            print(f"Invalid client_id: {self.client_id}")
            self.close(code=4004, reason='Invalid client_id')

    async def disconnect(self, close_code):
        try:
            if self.client_id in LobbyConsumer.list_of_users:

                # Acquire a lock before accessing/modifying shared data
                async with asyncio.Lock():
                    user = LobbyConsumer.list_of_users[self.client_id]
                    groups = user.get_groups()
                    for group in groups:
                        await group.remove_member(self.client_id, self.channel_name)
                        group_member_count = group.get_member_count()
                        if group_member_count == 0 and group.get_group_name() != 'website_lobby':
                            print(f"Group {group.get_group_name()} has no members, deleting group")
                            await self.delete_a_group(group.get_group_name())

                    LobbyConsumer.list_of_users.pop(self.client_id)

                print(f"User {self.client_id} disconnected")
            else:
                print("User not connected")

        except ValueError:
            print(f"Invalid client_id: {self.client_id}")
            self.close(code=4004, reason='Invalid client_id')

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', '')
            command = text_data_json.get('command', '')
            data = text_data_json.get('data', {})

            print(f"Received message: {text_data_json}")
            print(f"Message type: {message_type}")
            print(f"Command: {command}")
            print(f"Data: {data}")
            

            if message_type == 'command':
                await self.lobbycommands.execute_command(command, data)
            elif message_type == 'private_message':
                await self.send_private_message(data)
            elif message_type == 'group_message':
                await self.send_group_message(data)
            else:
                print("Invalid message type")

        except ValueError:
            print("Invalid JSON")
            await self.send_info_to_client('error', 'Invalid JSON')

    # Send information to client or group
    async def handle_group_info(self, event):
        """
        Handle group information received from the channel layer.
        This method will be invoked when a message with type 'handle_group_info' is received.
        """
        command = event['command']
        data = event['data']
        
        # Process the information as needed
        print(f'RECIEVED group information: {command}, {data}')
        # Send the information to the connected client
        await self.send_info_to_client(command, data)
    # Working
    async def send_info_to_client(self, command, data):
        print(f'SENDING: information to client: {command}, {data}')
        await self.send(text_data=json.dumps({
            'type': 'information',
            'command': command,
            'data': data,
    }))
    # Working
    async def send_info_to_group(self, group_name, command, data):
        print(f'SENDING: information to group: {group_name}, {command}, {data}')
        
        # Debug prints to check values before the call
        print(f'Command: {command}')
        print(f'Data: {data}')

        await self.channel_layer.group_send(
            group_name,
            {
                'type': 'handle_group_info',
                'command': command,
                'data': data,
        }
    )
    # -------------------------------

    # Send Messages to Client or Group 
    # Working
    async def handle_private_message(self, event):
        command = event['command']
        data = event['data']
        await self.send_info_to_client(command, data)
    # Working
    async def send_private_message(self, data):
        recipient_id = data.get('recipient_id')
        message = data.get('message')

        if recipient_id and message:
            recipient_channel = LobbyConsumer.list_of_channels.get(str(recipient_id))
            print(f"Recipient channel: {recipient_channel}")
            if recipient_channel:
                await self.channel_layer.send(
                    recipient_channel,
                    {
                        'type': 'handle_private_message',
                        'command': 'private_message',
                        'data': {
                            'sender_id': self.client_id,
                            'message': message,
                        }
                    }
                )
            else:
                await self.send_info_to_client('error', 'Recipient not found')
    # Working
    async def send_group_message(self, data):
        group_name = data.get('group_name')
        message = data.get('message')

        if group_name and message:
            group = LobbyConsumer.list_of_groups.get(group_name)
            if group:
                await group.broadcast('group_message', {
                    'sender_id': self.client_id,
                    'message': message,
                })
            else:
                await self.send_info_to_client('error', 'Group not found')
        else:
            await self.send_info_to_client('error', 'Invalid group message data')
    # -------------------------------

    # Class Groups Object Methods
    # Working
    async def create_a_group(self, room_name):
        print(f"Actual Creating and Sending: {room_name}")
        new_group = Group(room_name, self)

        async with asyncio.Lock():
            LobbyConsumer.list_of_groups.update({room_name: new_group})

        await self.channel_layer.group_add(
            room_name,
            self.channel_name,
        )
        await new_group.add_member(self.client_id, self.channel_name)
        self.user.add_group(new_group)
        await self.send_info_to_client('group_created', {'group_name': room_name})
        
        print(f"Group {room_name} created by {self.client_id}")
    #  Working
    async def delete_a_group(self, room_name):
        if room_name in LobbyConsumer.list_of_groups and room_name != 'website_lobby':
            group = LobbyConsumer.list_of_groups[room_name]
            members = group.get_all_member_ids()
            for member in members:
                await group.remove_member(member, LobbyConsumer.list_of_channels[member])
            await self.channel_layer.group_discard(
                room_name,
                self.channel_name,
            )

            async with asyncio.Lock():
                LobbyConsumer.list_of_groups.pop(room_name)

            await self.send_info_to_client('group_deleted', {'group_name': room_name})
            print(f"Group {room_name} deleted")
        else:
            if room_name == 'website_lobby':
                await self.send_info_to_client('error', f'Cannot delete group {room_name}')
                print(f"Cannot delete group {room_name}")
            else:
                await self.send_info_to_client('error', f'Group {room_name} does not exist')
                print(f"Group {room_name} does not exist")
    # Working
    async def change_group_name(self, old_room_name, new_room_name):
        if old_room_name in LobbyConsumer.list_of_groups:
            group = LobbyConsumer.list_of_groups[old_room_name]
            group.change_group_name(new_room_name)
            LobbyConsumer.list_of_groups.pop(old_room_name)
            LobbyConsumer.list_of_groups.update({new_room_name: group})
            print(f"Group {old_room_name} changed to {new_room_name}")
            await self.send_info_to_client('group_name_changed', {'old_group_name': old_room_name, 'new_group_name': new_room_name})
        else:
            print(f"Group {old_room_name} does not exist")
    # -------------------------------

    # Class Users Object Methods
    # Working
    async def create_a_user(self, client_id, channel_name):
        try:
            print(f"Creating user: {client_id}")
            if client_id in LobbyConsumer.list_of_users:
                await self.send_info_to_client('error', 'User already exists')
            else:
                # Check if the user model exists
                user_model = await self.get_user(int(client_id))

                if not user_model:
                    await self.send_info_to_client('error', 'User model does not exist')
                    print(f"User model does not exist for {client_id}")
                else:
                    new_user = User(client_id, channel_name, user_model, self)

                    async with asyncio.Lock():
                        LobbyConsumer.list_of_users.update({client_id: new_user})
                    
                    await self.send_info_to_client('user_created', {'user_id': client_id})
                    print(f"User {client_id} created")

        except ValueError:
            print(f"Invalid client_id: {client_id}")
            self.close(code=4004, reason='Invalid client_id')

