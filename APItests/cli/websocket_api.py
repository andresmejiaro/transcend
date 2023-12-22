# websocket_manager.py

import websockets
import json
import logging

class websocket_api:
    def __init__(self):
        self.websockets = {}
        self.logger = logging.getLogger("websocket_api")

    async def connect(self, url, query_params=None):
        try:
            if query_params:
                url += "?" + "&".join([f"{key}={value}" for key, value in query_params.items()])
            
            print(f'Connecting to {url}')

            websocket = await websockets.connect(url)
            self.websockets[url] = websocket  # Use URL as the key
            print(f'Current list of websockets: {self.websockets}')
            self.logger.info(f"Connected to {url}")
            return websocket
        except Exception as e:
            self.logger.error(f"Error connecting to {url}: {e}")
            raise

    async def close(self, url):
        try:
            websocket = self.websockets.get(url)
            if websocket:
                await websocket.close()
                del self.websockets[url]
                self.logger.info(f"Closed connection to {url}")
        except Exception as e:
            self.logger.error(f"Error closing connection: {e}")

    async def close_all(self):
        for url in list(self.websockets.keys()):
            await self.close(url)

    async def send(self, url, data):
        try:
            websocket = self.websockets.get(url)
            if websocket:
                if isinstance(data, dict):
                    data = json.dumps(data)
                await websocket.send(data)
                self.logger.info(f"Sent message to {url}")
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")

    async def receive(self, url):
        try:
            websocket = self.websockets.get(url)
            if websocket:
                data = await websocket.recv()
                self.logger.info(f"Received message from {url}")
                return json.loads(data)
        except Exception as e:
            self.logger.error(f"Error receiving message: {e}")
            raise
