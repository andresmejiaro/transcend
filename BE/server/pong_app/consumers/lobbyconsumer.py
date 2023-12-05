import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs

class LobbyConsumer(AsyncWebsocketConsumer):
    
    list_of_users = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = 'Website_Lobby'

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

        await self.accept()

        # Add the user to the list of users
        LobbyConsumer.list_of_users.append(self.client_id)

        await self.send(text_data=json.dumps({
            'action': 'connection',
            'message': f"You are connected to the game room {self.room_group_name}",
        }))

        # Announce to the group that a new player has joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_message',
                'data': {
                    'action': 'new_player',
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
                    'action': 'player_left',
                    'message': f"{self.client_id} has left {self.room_group_name}",
                }
            }
        )

    async def receive(self, text_data):
        # You can handle specific actions received from the client here
        data = json.loads(text_data)
        action = data['data'].get('action', '')

        print(f"Received message: {action}")

        if action == 'chat_message':
            # Broadcast chat messages to the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_message',
                    'data': {
                        'action': 'chat_message',
                        'message': data.get('message', ''),
                        'sender': self.client_id,
                    }
                }
            )

        if action == 'get_list_users':
            print(f"Sending list of users: {LobbyConsumer.list_of_users}")
            # Send list of users directly to the client that requested it
            await self.send(text_data=json.dumps({
                'action': 'list_users',
                'message': LobbyConsumer.list_of_users,
            }))

    async def broadcast_message(self, event):
        # Send the message to the WebSocket
        await self.send(text_data=json.dumps(event['data']))
