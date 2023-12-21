import asyncio
import websockets
import json

class PongGameClient:
    def __init__(self, websocket_uri_base):
        self.websocket_uri_base = websocket_uri_base
        self.websocket = None

    async def connect(self, match_id):
        uri = f"{self.websocket_uri_base}/{match_id}/"
        self.websocket = await websockets.connect(uri)
        print(f"Connected to Pong game WebSocket for match {match_id}")

    async def disconnect(self):
        if self.websocket:
            await self.websocket.close()
            print("Disconnected from Pong game WebSocket")

    async def play_pong(self, match_id):
        await self.connect(match_id)

        try:
            while True:
                # Your game logic goes here
                message = await self.websocket.recv()
                print(f"Received from Pong game WebSocket: {message}")

                # Simulate playing the game
                await asyncio.sleep(1)

        except websockets.WebSocketException as e:
            print(f"WebSocket connection error: {e}")

        finally:
            await self.disconnect()