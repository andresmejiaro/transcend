# network/client.py

import aiohttp

class GameClient:
    def __init__(self):
        self.session = None
        self.url = "http://localhost:8000"

    async def connect_to_server(self):
        self.session = aiohttp.ClientSession()