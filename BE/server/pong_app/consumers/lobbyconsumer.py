import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from .lobbyutils import LobbyCommands, LobbyFunctions
from api.userauth.models import CustomUser as User
import asyncio

class Group(object):
    def __init__(self, group_name):
        # String name of the group
        self.group_name = group_name
        # Dictionary of user_id: channel_name (channel_name is the channel name of the user's websocket connection)
        self.users = {}

    async def add_member(self, user_id, channel_name):
        # Check if user_id is already in the group
        print(f"In class Group, adding user_id: {user_id} with channel_name: {channel_name}")
        if user_id in self.users:
            return
        else:
            self.users[user_id] = channel_name
            await object.channel_layer.group_add(
                self.group_name ,
                channel_name,
            )
            # Announce to everyone in the group that someone has joined
            await object.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'information',
                    'command': 'user_joined',
                    'data': {
                        'user_id': user_id,
                    }
                }
            )

    async def remove_member(self, user_id, channel_name):
        if user_id in self.users:
            # Assuming some asynchronous operation, use "await" if needed
            del self.users[user_id]
            await self.channel_layer.group_discard(
                self.group_name,
                channel_name,
            )
            # Announce to everyone in the group that someone has left
            await object.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'information',
                    'command': 'user_left',
                    'data': {
                        'user_id': user_id,
                    }
                }
            )   
        else:
            print(f"User {user_id} not found in group {self.group_name}")

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
        print(self.users.values())
        list_of_members = {}
        for user_id, channel_name in self.users.items():
            list_of_members.update({user_id: channel_name})
        return list_of_members
        

    def get_group_name(self):
        return self.group_name
    
    async def change_group_name(self, group_name):
        self.group_name = group_name
        # Announce the group name change to everyone in the group
        await object.channel_layer.group_send(
            self.group_name,
            {
                'type': 'information',
                'command': 'group_name_changed',
                'data': {
                    'group_name': group_name,
                }
            }
        )

class User(object):
    def __init__(self, user_id, channel_name, user_model):
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
    website_lobby = Group('website_lobby')
    list_of_groups = {'website_lobby': website_lobby}
    list_of_users = {}
    list_of_channels = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lobbycommands = LobbyCommands(self)
        self.lobbyfunctions = LobbyFunctions(self)

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
                LobbyConsumer.list_of_channels[self.client_id] = self.channel_name

                if user_model:
                    print(f"User {self.client_id} connected")
                    self.user = User(self.client_id, self.channel_name, user_model)
                    self.user.add_group(LobbyConsumer.website_lobby)
                    # Make a channel layer group for the user
                    await self.channel_layer.group_add(
                        user_model.username,
                        self.user.get_channel_name(),
                    )

                    # Add the user to the list of users
                    async with asyncio.Lock():
                        LobbyConsumer.list_of_users.update({self.client_id: self.user})

                    LobbyConsumer.website_lobby.add_member(self.user.get_user_id(), self.user.get_channel_name())
                    await self.accept()
                    print(f"User {self.client_id} added to website_lobby with channel_name: {self.channel_name} and user_model: {user_model} with type: {type(user_model)}")

        except ValueError:
            print(f"Invalid client_id: {self.client_id}")
            self.close(code=4004, reason='Invalid client_id')

    async def disconnect(self, close_code):
        if self.client_id in LobbyConsumer.list_of_users:
            user = LobbyConsumer.list_of_users[self.client_id]
            groups = user.get_groups()
            print(type(groups))  # This should print <class 'list'>

            for group in groups:
                group.remove_member(self.client_id, self.channel_name)
                group_member_count = group.get_member_count()
                if group_member_count == 0:
                    self.delete_a_group(group.get_group_name())
        
            async with asyncio.Lock():
                LobbyConsumer.list_of_users.pop(self.client_id)

            print(f"User {self.client_id} disconnected")
        else:
            print("User not connected")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', '')
        command = text_data_json.get('command', '')
        data = text_data_json.get('data', {})

        print(f"Received message: {text_data_json}")
        print(f"Message type: {message_type}")
        print(f"Command: {command}")
        print(f"Data: {data}")

        if message_type == 'command':
            # Call the appropriate command based on the received data
            await self.lobbycommands.execute_command(command, data)
        else:
            print("Invalid message type")

    # Group
    async def create_a_group(self, room_name):
        if room_name in LobbyConsumer.list_of_groups:
            print(f"Group {room_name} already exists")
        else:
            new_group = Group(room_name)
            LobbyConsumer.list_of_groups.update({room_name: new_group})
            await self.channel_layer.group_add(
                room_name,
                self.channel_name,
            )
            print(f"Group {room_name} created by {self.client_id}")

    async def delete_a_group(self, room_name):
        if room_name in LobbyConsumer.list_of_groups:
            group = LobbyConsumer.list_of_groups[room_name]
            members = group.get_all_member_ids()
            for member in members:
                await group.remove_member(member, LobbyConsumer.list_of_channels[member])
            await self.channel_layer.group_discard(
                room_name,
                self.channel_name,
            )
            LobbyConsumer.list_of_groups.pop(room_name)
            print(f"Group {room_name} deleted")
        else:
            print(f"Group {room_name} does not exist")

    async def change_room_name(self, old_room_name, new_room_name):
        if old_room_name in LobbyConsumer.list_of_groups:
            group = LobbyConsumer.list_of_groups[old_room_name]
            group.change_group_name(new_room_name)
            LobbyConsumer.list_of_groups.pop(old_room_name)
            LobbyConsumer.list_of_groups.update({new_room_name: group})
            print(f"Group {old_room_name} changed to {new_room_name}")
        else:
            print(f"Group {old_room_name} does not exist")

    async def remove_user_from_all_groups(self, user_id):
        if user_id in LobbyConsumer.list_of_users:
            user = LobbyConsumer.list_of_users[user_id]
            groups = user.get_groups()
            for group in groups:
                await group.remove_member(user_id, LobbyConsumer.list_of_channels[user_id])
                if group.get_member_count() == 0:
                    await self.delete_a_group(group.get_group_name())
                else:
                    await self.send_user_count(group.get_group_name(), group.get_member_count())

            print(f"User {user_id} removed from all groups")
        else:
            print(f"User {user_id} does not exist")


    # User
    async def create_a_user(self, user_id, channel_name, user_model):
        if user_id not in LobbyConsumer.list_of_users:
            user = User(user_id, channel_name, user_model)
            LobbyConsumer.list_of_users.update({user_id: user})
            print(f"User {user_id} created")
        else:
            print(f"User {user_id} already exists")

    async def delete_a_user(self, user_id):
        if user_id in LobbyConsumer.list_of_users:
            LobbyConsumer.list_of_users.pop(user_id)
            print(f"User {user_id} deleted")
        else:
            print(f"User {user_id} does not exist")

    # Information
    async def send_info_to_client(self, command, data):
        print(f'SENDING: information to client: {command}, {data}')
        await self.send(text_data=json.dumps({
            'type': 'information',
            'command': command,
            'data': data,
        }))

    async def send_info_to_group(self, group_name, command, data):
        await self.channel_layer.group_send(
            group_name,
            {
                'type': 'information',
                'command': command,
                'data': data,
            }
        )