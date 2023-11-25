from django.urls import path
from .views import *


urlpatterns = [
    # Tournament
    path('tournament/create/', tournament_create, name="create"),
    path('tournament/', tournament_list, name="list"),
    path('tournament/<int:pk>/', tournament_operations, name="detail"),
    path('tournament/<int:pk>/rounds/', tournament_rounds, name="round"),
    # Match
    path('match/create/', match_create, name='creatematch'),
    path('match/', match_list, name='listmatches'),
    path('match/<int:pk>/', match_operations, name="team_detail"),
    # Round
    path('round/create/', round_create, name='round_create'),
    path('round/', round_list, name='round_list'),
    path('round/<int:pk>/', round_operations, name="round_detail"),
    # User
    path('user/create/', user_create, name='user_create'),
    path('user/', user_list, name='user_list'),
    path('user/<int:pk>/', user_operations, name='user_detail'),
    path('user/<int:pk>/match/', user_all_matches, name='user_match'),
    path('user/<int:pk>/tournament/', user_all_tournaments, name='user_tournament'),
    
    # Matchmaking for Tournaments
    # <int:pk> is the tournament id
    path('tournament/<int:pk>/matchmaking/', game_matchmaking, name='game_matchmaking'),
]
