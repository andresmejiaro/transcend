import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from ws_api.python_pong.Player import Player
from ws_api.python_pong.Game import Game
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.utils import timezone
# Icecream is a library that allows us to ic variables in a more readable way its is only for debugging and can be removed
from icecream import ic

class TournamentConsumer(AsyncWebsocketConsumer):

    list_of_players = {}
    list_of_matches = {}
    list_of_rounds = {}
    

    async def connect(self):
        pass

    async def disconnect(self, code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        pass