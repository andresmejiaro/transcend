# ws_api/urls.py

from django.urls import path
from .views import pong_game

urlpatterns = [
    path('pong/<str:room_name>/', pong_game, name="pong"),
]
