from django.urls import re_path
from .consumers.lobbyconsumer import LobbyConsumer
from .consumers.gameconsumerasbride import GameConsumerAsBridge


websocket_pong_urlpatterns = [
    re_path(r"^ws/lobby/$", LobbyConsumer.as_asgi()),
    re_path(r"^ws/pong/(?P<match_id>\w+)/$", GameConsumerAsBridge.as_asgi()),
]