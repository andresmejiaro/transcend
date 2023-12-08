from django.urls import re_path

from .consumers.gameconsumers import PongConsumer
from .consumers.lobbyconsumer import LobbyConsumer
from .consumers.gameconsumer_idea2 import MatchConsumer

websocket_pong_urlpatterns = [
    re_path(r"^ws/lobby/$", LobbyConsumer.as_asgi()),
    re_path(r"^ws/pong/(?P<match_id>\w+)/$", MatchConsumer.as_asgi()),
]