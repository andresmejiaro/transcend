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
    # The first time you call this, it will determine the number of rounds needed per the amount of players
    # It will then create the rounds and matches for each round
    # It will then return the first round of matches
    # You can then call this again to get the next round of matches until there are no more rounds
    # If you call this again after all rounds have been played, it will return a the winner of the tournament
    path('tournament/<int:pk>/matchmaking/', game_matchmaking, name='game_matchmaking'),
]
