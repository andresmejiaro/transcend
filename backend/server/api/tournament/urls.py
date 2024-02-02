from django.urls import path
from .views import *


urlpatterns = [
    # Tournament
    path('tournament/create/', tournament_create, name="create"),
    # path('tournament/', tournament_list, name="list"),
    path('tournament/<int:pk>/', tournament_operations, name="detail"),
    path('tournament/<int:pk>/rounds/', tournament_rounds, name="round"),
    # Match
    path('match/create/', match_create, name='creatematch'),
    path('match/', match_list, name='listmatches'),
    # path('match/<int:match_id>/', match_list, name='listmatches'),
    path('match/available/', match_available, name='available'),
    path('match/<int:match_id>/', get_match_info, name="match_info"),
    # Round
    path('round/create/', round_create, name='round_create'),
    path('round/', round_list, name='round_list'),
    path('round/<int:pk>/', round_operations, name="round_detail"),
    # User
    path('user/create/', user_create, name='user_create'),
    path('user/', user_list, name='user_list'),
    path('user/<int:pk>/', user_operations, name='user_detail'),
    path('user/match/', user_all_matches, name='user_match'),
    path('user/match/<str:username>/', user_all_matches_username, name='user_match_username'),
    path('user/<int:pk>/tournament/', user_all_tournaments, name='user_tournament'),
    
    # Matchmaking for Tournaments
    path('tournament/', list_joinable_tournaments, name="list_joinable_tournaments"),
    path('tournament/<str:name>/', get_tournament_by_name, name="get_tournament_by_name"),
]
