# ws_api/routing.py

from django.urls import re_path
from .consumers.lobbyconsumer import LobbyConsumer as LobbyConsumer
from .consumers.gameconsumerasbride import GameConsumerAsBridge
from .consumers.tournamentconsumer import TournamentConsumer
from .consumers.gameconsumer2 import PongConsumer

websocket_pong_urlpatterns = [
    re_path(r"^ws/lobby/$", LobbyConsumer.as_asgi()),
    re_path(r"^ws/pong/(?P<match_id>\w+)/$", GameConsumerAsBridge.as_asgi()),
    re_path(r"^ws/tournament/(?P<tournament_id>\w+)/$", TournamentConsumer.as_asgi()),
    re_path(r"^ws/pong2/(?P<match_id>\w+)/$", PongConsumer.as_asgi()),
    
]