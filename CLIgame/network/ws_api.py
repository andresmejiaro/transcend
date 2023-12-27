# network/ws_api.py:

from utils.data_storage import load_data, save_data
from utils.logger import log_message
import logging
import websockets
import json

API_WS_URL = "ws://localhost:8001/ws"
DATA_DIR = "data"

class websocket_api:
    def __init__(self):
        self.list_of_websockets = {}

# Connection methods
    async def connect(self, url, query_params=None):
        try:
            if query_params:
                # Construct query string from query_params
                query_string = "&".join([f"{key}={value}" for key, value in query_params.items()])
                url += f"?{query_string}"

            websocket = await websockets.connect(url)
            self.list_of_websockets[url] = websocket

            log_message(f"Connected to {url}", level=logging.INFO)

            return websocket
        
        except Exception as e:
            log_message(f"Error connecting to {url}: {e}", level=logging.ERROR)
            raise

    async def close(self, websocket):
        try:
            if websocket:
                await websocket.close()
                log_message(f"Closed connection to {websocket.remote_address}", level=logging.INFO)

        except Exception as e:
            log_message(f"Error closing connection to {websocket.remote_address}: {e}", level=logging.ERROR)
            raise

    async def send(self, websocket, data):
        try:
            if websocket:
                if isinstance(data, dict):
                    data = json.dumps(data)
                await websocket.send(data)
                log_message(f"Sent message: {data}", level=logging.INFO)
                
        except Exception as e:
            log_message(f"Error sending message: {e}", level=logging.ERROR)
            raise

    async def receive(self, websocket):
        try:
            data = await websocket.recv()
            log_message(f"Received message: {data}", level=logging.INFO)
            return data
        except Exception as e:
            log_message(f"Error receiving message: {e}", level=logging.ERROR)
            raise
# -----------------------------

# Predifined websocket requests and responses       
    async def get_online_users(self, websocket):
        try:
            data = await self.send(websocket, {"command": "list_of_users"})
            return data
        except Exception as e:
            log_message(f"Error sending message: {e}", level=logging.ERROR)
            raise

    async def get_user_info(self, websocket, username):
        try:
            data = await self.send(websocket, {"command": "user_info", "username": username})
            return data
        except Exception as e:
            log_message(f"Error sending message: {e}", level=logging.ERROR)
            raise
# -----------------------------
