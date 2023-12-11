# ws_api/views.py

from django.shortcuts import render

def pong_game(request, room_name):
    return render(request, "ws_api/pong_game.html", {"room_name": room_name})
