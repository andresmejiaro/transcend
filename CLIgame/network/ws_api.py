# network/ws_api.py:

from utils.data_storage import load_data, save_data
from utils.logger import log_message
import logging
import websockets
import json

class websocket_api:
    def __init__(self):
        self.websocket_connections = {}  # Dictionary to store WebSocket instances by name

    async def connect(self, connection_name, url):
        try:
            if connection_name not in self.websocket_connections or self.websocket_connections[connection_name].closed:
                websocket = await websockets.connect(url)
                self.websocket_connections[connection_name] = websocket
                log_message(f"Connected to WebSocket ({connection_name}): {url}", level=logging.INFO)
        except Exception as e:
            log_message(f"Error connecting to WebSocket ({connection_name}): {e}", level=logging.ERROR)

    async def disconnect(self, connection_name):
        try:
            if connection_name in self.websocket_connections:
                await self.websocket_connections[connection_name].close()
                del self.websocket_connections[connection_name]
                log_message(f"Disconnected from WebSocket ({connection_name})", level=logging.INFO)
        except Exception as e:
            log_message(f"Error disconnecting from WebSocket ({connection_name}): {e}", level=logging.ERROR)

    async def send_message(self, connection_name, data):
        try:
            if connection_name in self.websocket_connections:
                await self.websocket_connections[connection_name].send(json.dumps(data))
                log_message(f"Sent message to WebSocket ({connection_name}): {data}", level=logging.INFO)
        except Exception as e:
            log_message(f"Error sending message to WebSocket ({connection_name}): {e}", level=logging.ERROR)

    async def receive_messages(self, connection_name):
        try:
            while connection_name in self.websocket_connections:
                data = await self.websocket_connections[connection_name].recv()
                log_message(f"Received message from WebSocket ({connection_name}): {data}", level=logging.INFO)
                # Handle the received message as needed
                return data
        except Exception as e:
            log_message(f"Error receiving messages from WebSocket ({connection_name}): {e}", level=logging.ERROR)

    async def receive_messages_forever(self, connection_name, callback):
        try:
            while connection_name in self.websocket_connections:
                data = await self.websocket_connections[connection_name].recv()
                log_message(f"Received message from WebSocket ({connection_name}): {data}", level=logging.INFO)
                await callback(data)
        except Exception as e:
            log_message(f"Error receiving messages from WebSocket ({connection_name}): {e}", level=logging.ERROR)
            
    async def receive_messages_until(self, connection_name, condition):
        try:
            while connection_name in self.websocket_connections:
                data = await self.websocket_connections[connection_name].recv()
                log_message(f"Received message from WebSocket ({connection_name}): {data}", level=logging.INFO)
                # Handle the received message as needed
                if condition(data):
                    break
        except Exception as e:
            log_message(f"Error receiving messages from WebSocket ({connection_name}): {e}", level=logging.ERROR)

    async def connected(self, connection_name):
        return connection_name in self.websocket_connections and not self.websocket_connections[connection_name].closed