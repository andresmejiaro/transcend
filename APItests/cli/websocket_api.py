# websocket_manager.py

import websockets
import json
import logging

class websocket_api:
    def __init__(self):
        self.logger = logging.getLogger("websocket_api")

    async def connect(self, url, query_params=None):
        try:
            if query_params:
                url += "?" + "&".join([f"{key}={value}" for key, value in query_params.items()])
            
            # print(f'Connecting to {url}')

            websocket = await websockets.connect(url)
            self.logger.info(f"Connected to {url}")
            return websocket
        except Exception as e:
            self.logger.error(f"Error connecting to {url}: {e}")
            raise

    async def close(self, websocket):
        try:
                await websocket.close()
                self.logger.info(f"Closed connection to {websocket}")

        except Exception as e:
            self.logger.error(f"Error closing connection: {e}")
            raise

    async def send(self, websocket, data):
        try:
            if websocket:
                if isinstance(data, dict):
                    data = json.dumps(data)
                await websocket.send(data)
                self.logger.info(f"Sent message: {data}")
                
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")

    async def receive(self, websocket):
        try:
            data = await websocket.recv()
            self.logger.info(f"Received message: {data}")
            return data
        except Exception as e:
            self.logger.error(f"Error receiving message: {e}")
            raise

# Predifined websocket requests and responses
        
    async def get_online_users(self, websocket):
        try:
            data = await self.send(websocket, {"command": "list_of_users"})
            return data
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            raise