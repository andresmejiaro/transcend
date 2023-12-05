import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs
from channels.db import database_sync_to_async


class LobbyConsumer(AsyncWebsocketConsumer):
    
    list_of_users = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = 'Website_Lobby'

    @database_sync_to_async
    def get_user(self, client_id):
        from api.userauth.models import CustomUser as User
        user = User.objects.get(client_id=client_id)
        if user:
            return user
        else:
            return None

    async def connect(self):
        # parse the query string to find client_id
        query_string = self.scope['query_string'].decode('utf-8')
        query_params = parse_qs(query_string)
        self.client_id = query_params.get('client_id', [''])[0]

        # Add the user to the game room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Check if the client_id belongs to a user


        # Check if the user is already in the list of users
        if self.client_id in LobbyConsumer.list_of_users:
            # Reject the connection
            await self.close()
        else:
            await self.accept()

        # Add the user to the list of users
        LobbyConsumer.list_of_users.append(self.client_id)

        await self.send(text_data=json.dumps({
            'message': f"You are connected to the game room {self.room_group_name}",
        }))

        # Announce to the group that a new player has joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_message',
                'data': {
                    'message': f"{self.client_id} has joined {self.room_group_name}",
                }
            }
        )

    async def disconnect(self, close_code):
        # Remove the user from the game room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        # Remove the user from the list of users
        LobbyConsumer.list_of_users.remove(self.client_id)

        # Announce to the group that a player has left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_message',
                'data': {
                    'message': f"{self.client_id} has left {self.room_group_name}",
                }
            }
        )

    async def receive(self, text_data):
        # You can handle specific actions received from the client here
        data = json.loads(text_data)
        message_type = data.get('type', '')

        print(f"Received data whole: {data}")
        print(f"Received type: {message_type}")

        if message_type == 'chat_message':
            # Broadcast chat messages to the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_message',
                    'data': {
                        'message': data.get('data', {}).get('message', ''),
                        'sender': self.client_id,
                    }

                }
            )

        elif message_type == 'get_list_users':
            print(f"Sending list of users: {LobbyConsumer.list_of_users}")
            # Send list of users directly to the client that requested it
            await self.send(text_data=json.dumps({
                'type': 'list_of_users',  # This is a custom type that we defined
                'data': {
                    'message': LobbyConsumer.list_of_users,
                }
            }))

        elif message_type == 'ping':
            # Send a pong message back to the client
            await self.send(text_data=json.dumps({
                'type': 'pong',
                'data': {
                    'message': 'pong',
                }
            }))

        elif message_type == 'private_message':
            # Send a private message to a specific client
            recipient_client_id = data.get('data', {}).get('recipient_client_id', '')
            message = data.get('data', {}).get('message', '')
            await self.channel_layer.send(
                f"ws.{recipient_client_id}",
                {
                    'type': 'broadcast_message',
                    'data': {
                        'message': message,
                        'sender': self.client_id,
                    }
                }
            )

    async def broadcast_message(self, event):
        # Check if the event contains a 'data' key
        if 'data' in event:
            data = event['data']
        else:
            data = event

        message_type = data.get('type', '')

        # Handle regular and private messages differently
        if message_type == 'chat_message':
            # Broadcast chat messages to the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_message',
                    'data': {
                        'message': data.get('data', {}).get('message', ''),
                        'sender': data.get('data', {}).get('sender', ''),
                    }
                }
            )

        elif message_type == 'private_message':
            recipient_channel_name = data.get('data', {}).get('recipient_channel_name', '')
            message = data.get('data', {}).get('message', '')
            
            # Send a private message to a specific client
            await self.channel_layer.send(
                recipient_channel_name,
                {
                    'type': 'broadcast_message',
                    'data': {
                        'message': message,
                        'sender': data.get('data', {}).get('sender', ''),
                    }
                }
            )

        else:
            # Send the message to the WebSocket
            await self.send(text_data=json.dumps(data))


