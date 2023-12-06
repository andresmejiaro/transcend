from django.urls import re_path

from .consumers.gameconsumers import PongConsumer
from .consumers.lobbyconsumer import LobbyConsumer

websocket_pong_urlpatterns = [
    re_path(r"^ws/lobby/$", LobbyConsumer.as_asgi()),
    re_path(r"^ws/pong/(?P<room_name>\w+)/$", PongConsumer.as_asgi()),
]