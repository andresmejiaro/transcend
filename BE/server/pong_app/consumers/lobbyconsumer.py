import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from channels.db import database_sync_to_async

class LobbyConsumer(AsyncWebsocketConsumer):

    global_lobby_group = 'Website_Lobby'
    list_of_user_ids = []
    list_of_user_channels = {}
    list_of_user_objects = {}
    list_of_groups = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @database_sync_to_async
    def get_user(cls, client_id):
        from api.userauth.models import CustomUser as User
        try:
            user = User.objects.get(pk=client_id)
            return user
        except User.DoesNotExist:
            return

    async def connect(self):
        query_string = self.scope['query_string'].decode('utf-8')
        query_params = parse_qs(query_string)
        self.client_id = query_params.get('client_id', [''])[0]

        await self._join_global_lobby_group()
        await self._join_own_group()

        if self.client_id not in self.list_of_user_ids:
            await self._accept_connection()
            await self._announce_user_join()
        else:
            self.close(code=4004, reason='User already connected')

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', '')

        print(f"Received type: {message_type}")

        if message_type == 'lobby_message':
            await self._broadcast_site_wide_message(data)
        elif message_type == 'get_list_users':
            await self._send_list_of_users()
        elif message_type == 'get_list_user_channels':
            await self._send_list_of_user_channels()
        elif message_type == 'get_list_of_groups':
            await self._send_list_of_groups()
        elif message_type == 'ping':
            await self._send_pong()
        elif message_type == 'create_group':
            await self._handle_create_group(data)
        elif message_type == 'join_group':
            await self._handle_join_group(data)
        elif message_type == 'leave_group':
            await self._leave_group(data.get('data', {}).get('group_name', ''))
        elif message_type == 'leave_all_groups':
            await self.leave_all_groups()
        elif message_type == 'remove_user_from_group':
            await self._remove_user_from_group(data.get('data', {}).get('group_name', ''), data.get('data', {}).get('user_id', ''))
        elif message_type == 'send_private_message':
            await self._send_private_message(data)
        elif message_type == 'send_message_to_group':
            await self._send_message_to_group(data)
        elif message_type == 'invite_to_group':
            await self._invite_to_group(data)


    async def leave_all_groups(self):
        await self._leave_group(self.global_lobby_group)
        await self._leave_group(self.client_id)

        self.list_of_user_ids.remove(self.client_id)
        del self.list_of_user_channels[self.client_id]
        del self.list_of_user_objects[self.client_id]

        for group_name, group_info in self.list_of_groups.items():
            await self._remove_user_from_group(group_name, self.client_id)

    async def disconnect(self, close_code):
        await self.leave_all_groups()
        await self._announce_user_leave()

    async def lobby_message(self, event):
        data = event['data']
        await self.send(text_data=json.dumps({
            'type': 'lobby_message',
            'data': data,
        }))

    async def _join_global_lobby_group(self):
        await self.channel_layer.group_add(
            self.global_lobby_group,
            self.channel_name
        )

    async def _join_own_group(self):
        await self.channel_layer.group_add(
            self.client_id,
            self.channel_name
        )

    async def _accept_connection(self):
        await self.accept()
        LobbyConsumer.list_of_user_ids.append(self.client_id)
        LobbyConsumer.list_of_user_channels[self.client_id] = self.channel_name
        self.user_object = await self.get_user(self.client_id)
        LobbyConsumer.list_of_user_objects[self.client_id] = self.user_object

        if LobbyConsumer.global_lobby_group not in LobbyConsumer.list_of_groups:
            LobbyConsumer.list_of_groups[LobbyConsumer.global_lobby_group] = {'members': []}
        LobbyConsumer.list_of_groups[LobbyConsumer.global_lobby_group]['members'].append(self.client_id)

    async def _announce_user_join(self):
        await self.channel_layer.group_send(
            self.global_lobby_group,
            {
                'type': 'lobby_message',
                'data': {
                    'message': f"{self.user_object.username} has joined {LobbyConsumer.global_lobby_group}",
                }
            }
        )

    async def _announce_user_leave(self):
        await self.channel_layer.group_send(
            self.global_lobby_group,
            {
                'type': 'lobby_message',
                'data': {
                    'message': f"{self.user_object.username} has left {LobbyConsumer.global_lobby_group}",
                }
            }
        )

    async def _broadcast_site_wide_message(self, data):

        await self.channel_layer.group_send(
            self.global_lobby_group,
            {
                'type': 'lobby_message',
                'data': {
                    'message': data.get('data', {}).get('message', ''),
                    'sender': self.client_id,
                }
            }
        )

    async def _send_list_of_users(self):
        await self.send(text_data=json.dumps({
            'type': 'list_of_user_ids',
            'data': {
                'message': self.list_of_user_ids,
            }
        }))

    async def _send_list_of_user_channels(self):
        await self.send(text_data=json.dumps({
            'type': 'list_of_user_channels',
            'data': {
                'message': self.list_of_user_channels,
            }
        }))

    async def _send_list_of_groups(self):
        await self.send(text_data=json.dumps({
            'type': 'list_of_groups',
            'data': {
                'message': self.list_of_groups,
            }
        }))

    async def _send_pong(self):
        await self.send(text_data=json.dumps({
            'type': 'ping',
            'data': {
                'message': 'pong',
            }
        }))

    async def _handle_create_group(self, data):
        group_name = data.get('data', {}).get('group_name', '')
        await self._create_group(group_name)
        await self.send(text_data=json.dumps({
            'type': 'group_created',
            'data': {
                'message': f"You have created and joined {group_name}",
            }
        }))

    async def _handle_join_group(self, data):
        group_name = data.get('data', {}).get('group_name', '')
        if group_name not in self.list_of_groups:
            await self.send(text_data=json.dumps({
                'type': 'group_not_exist',
                'data': {
                    'message': f"{group_name} does not exist",
                }
            }))
            return
        await self._join_group(group_name)
        await self.send(text_data=json.dumps({
            'type': 'group_joined',
            'data': {
                'message': f"You have joined {group_name}",
            }
        }))

    async def _leave_group(self, group_name):
        await self.channel_layer.group_discard(
            group_name,
            self.channel_name
        )

    async def _remove_user_from_group(self, group_name, user_id):
        if group_name in self.list_of_groups and 'members' in self.list_of_groups[group_name]:
            members = self.list_of_groups[group_name]['members']
            if user_id in members:
                members.remove(user_id)

    async def _create_group(self, group_name):
        await self.channel_layer.group_add(
            group_name,
            self.channel_name
        )
        self.list_of_groups[group_name] = {'members': [self.client_id]}

    async def _join_group(self, group_name):
        await self.channel_layer.group_add(
            group_name,
            self.channel_name
        )
        if group_name in self.list_of_groups:
            self.list_of_groups[group_name]['members'].append(self.client_id)
        else:
            self.list_of_groups[group_name] = {'members': [self.client_id]}

    async def _send_private_message(self, data): 
        user_id = data.get('data', {}).get('user_id', '')
        message = data.get('data', {}).get('message', '')
        if user_id in self.list_of_user_channels:
            await self.channel_layer.send(
                LobbyConsumer.list_of_user_channels[user_id],
                {
                    'type': 'private_message',
                    'data': {
                        'message': message,
                        'sender': self.client_id,
                    }
                }
            )
        else:
            await self.send(text_data=json.dumps({
                'type': 'user_not_exist',
                'data': {
                    'message': f"{user_id} does not exist",
                }
            }))

    async def private_message(self, event):
        data = event['data']
        await self.send(text_data=json.dumps({
            'type': 'private_message',
            'data': data,
        }))

    async def _send_message_to_group(self, data):
        group_name = data.get('data', {}).get('group_name', '')
        message = data.get('data', {}).get('message', '')
        if group_name in self.list_of_groups:
            members = self.list_of_groups[group_name]['members']
            for member in members:
                if member in self.list_of_user_channels:
                    await self.channel_layer.send(
                        LobbyConsumer.list_of_user_channels[member],
                        {
                            'type': 'group_message',
                            'data': {
                                'message': message,
                                'sender': self.client_id,
                            }
                        }
                    )
        else:
            await self.send(text_data=json.dumps({
                'type': 'group_not_exist',
                'data': {
                    'message': f"{group_name} does not exist",
                }
            }))

    async def group_message(self, event):
        data = event['data']
        await self.send(text_data=json.dumps({
            'type': 'group_message',
            'data': data,
        }))

    async def _invite_to_group(self, data):
        group_name = data.get('data', {}).get('group_name', '')
        user_id = data.get('data', {}).get('user_id', '')
        if group_name in self.list_of_groups and user_id in self.list_of_user_channels:
            await self.channel_layer.send(
                LobbyConsumer.list_of_user_channels[user_id],
                {
                    'type': 'invite_to_group',
                    'data': {
                        'group_name': group_name,
                        'sender': self.client_id,
                    }
                }
            )
        else:
            await self.send(text_data=json.dumps({
                'type': 'group_not_exist',
                'data': {
                    'message': f"{group_name} does not exist",
                }
            }))

    async def invite_to_group(self, event):
        data = event['data']
        await self.send(text_data=json.dumps({
            'type': 'invite_to_group',
            'data': data,
        }))
