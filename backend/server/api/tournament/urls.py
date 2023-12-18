from django.urls import path
from .views.match_view import match_create, match_list, match_operations, match_available
from .views.round_view import round_create, round_list, round_operations
from .views.tournament_view import tournament_create, tournament_list, tournament_operations, tournament_rounds
from .views.user_view import user_create, user_list, user_operations, user_all_matches, user_all_tournaments, user_stats


urlpatterns = [
    # Tournament
    path('tournament/create/', tournament_create, name="create"),
    path('tournament/', tournament_list, name="list"),
    path('tournament/<int:pk>/', tournament_operations, name="detail"),
    path('tournament/<int:pk>/rounds/', tournament_rounds, name="round"),
    # Match
    path('match/create/', match_create, name='creatematch'),
    path('match/', match_list, name='listmatches'),
    path('match/available/', match_available, name='available'),
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
    path('user/<int:pk>/stats/', user_stats, name='user_stats'),
]
