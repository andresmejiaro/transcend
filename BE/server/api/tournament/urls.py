from django.urls import path
from .views import *


urlpatterns = [
    path('create/', touprnament_create, name="create"),
    path('list/', tournament_list, name="list"),
    path('delete/<int:tournament_id>/', tournament_delete, name='tournament_delete'),
    path('update/<int:tournament_id>/', tournament_update, name='tournament_update'),
    path('creatematch/', match_create, name='creatematch'),
    path('listmatches/', match_list, name='listmatches'),
    path('deletematch/<int:match_id>/', match_delete, name='deletematch'),
    path('updatematch/<int:match_id>/', match_update, name='updatematch'),
]
