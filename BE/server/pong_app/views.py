# pong_app/views.py

from django.shortcuts import render

def pong_game(request, room_name):
    return render(request, "pong_app/pong_game.html", {"room_name": room_name})
