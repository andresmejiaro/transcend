from django.urls import path
from .views import *


urlpatterns = [
    path('tournament/create/', tournament_create, name="create"),
    path('tournament/', tournament_list, name="list"),
    path('tournament/<int:pk>/', tournament_operations, name="detail"),

    path('match/create/', match_create, name='creatematch'),
    path('match/', match_list, name='listmatches'),
    path('match/<int:pk>/', match_operations, name="team_detail"),

    path('round/create/', round_create, name='round_create'),
    path('round/', round_list, name='round_list'),
    path('round/<int:pk>/', round_operations, name="round_detail"),

    path('user/create/', user_create, name='user_create'),
    path('user/', user_list, name='user_list'),
    path('user/<int:pk>/', user_operations, name='user_detail'),
    # path('user/<int:pk>/', user_detail_update_delete, name='user_delete'),
    # path('user/<int:pk>/', user_detail_update_delete, name='user_update'),

    path('game/matchmaking/<int:pk>/', game_matchmaking, name='game_matchmaking'),
]
