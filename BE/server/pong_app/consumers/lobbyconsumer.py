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

    async def remove_member(self, user_id, channel_name):
        if user_id in self.users:
            # Assuming some asynchronous operation, use "await" if needed
            del self.users[user_id]
            await self.channel_layer.group_discard(
                self.group_name,
                channel_name,
            )
        else:
            print(f"User {user_id} not found in group {self.group_name}")

    def get_member_count(self):
        # Return the number of users in the group
        return len(self.users)

    def get_all_user_ids(self):
        # Return a list of user_ids in the group
        return list(self.users.keys())

    def get_channel_name(self, user_id):
        # Return the channel_name of the user_id
        return self.users.get(user_id)

    def get_channel_all_names(self):
        # Return a list of channel_names in the group
        return list(self.users.values())

    def get_group_name(self):
        return self.group_name
    
    def change_group_name(self, group_name):
        self.group_name = group_name

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
                    print(f"User {self.client_id} created")
                    self.user.add_group(LobbyConsumer.website_lobby)
                    print(f"User {self.client_id} added to website_lobby")
                    # Make a channel layer group for the user
                    print(f"Adding user {self.client_id} to channel_layer group {self.user.get_channel_name()}")
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
                await group.remove_member(self.client_id, self.channel_name)
                await self._send_group_member_count(group.get_group_name(), group.get_member_count())

            async with asyncio.Lock():
                LobbyConsumer.list_of_users.pop(self.client_id)

            await self.lobbyfunctions._send_user_list()
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

    # async def _send_group_member_count(self, group_name, member_count):
    #     await self.send(text_data=json.dumps({
    #         'type': 'group_member_count',
    #         'group_name': group_name,
    #         'member_count': member_count
    #     }))

    # async def _send_group_member_list(self, group_name, member_list):
    #     await self.send(text_data=json.dumps({
    #         'type': 'group_member_list',
    #         'group_name': group_name,
    #         'member_list': member_list
    #     }))

    # async def _send_user_list(self):
    #     user_list = []
    #     for user in LobbyConsumer.list_of_users.values():
    #         user_list.append(user.get_user_id())

    #     await self.send(text_data=json.dumps({
    #         'type': 'user_list',
    #         'user_list': user_list
    #     }))

    # async def _send_message(self, group_name, message):
    #     # Check if the group_name is a group or a user for private messaging
    #     print(f'Sending message: {message} to group: {group_name} with type: {type(group_name)}')
    #     if group_name in LobbyConsumer.list_of_groups:
    #         print("SENDING MESSAGE TO GROUP")
    #         await self.channel_layer.group_send(
    #             group_name,
    #             {
    #                 'type': 'lobby_message',
    #                 'message': message
    #             }
    #         )
    #     elif group_name in LobbyConsumer.list_of_channels:
    #         print("SENDING MESSAGE TO USER")
    #         recipient_channel_name = LobbyConsumer.list_of_channels[group_name]
    #         await self.channel_layer.send(
    #             recipient_channel_name,
    #             {
    #                 'type': 'lobby_message',
    #                 'message': message
    #             }
    #         )
    #     else:
    #         print("Invalid recipient: ", group_name)

    #     # echo message back to sender
    #     await self.send(text_data=json.dumps({
    #         'type': 'lobby.message',
    #         'message': message
    #     }))

    # async def lobby_message(self, event):
    #     print("Sending lobby message")
    #     message = event['message']
    #     await self.send(text_data=json.dumps({
    #         'type': 'lobby.message',
    #         'message': message
    #     }))
