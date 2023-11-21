from django.urls import path
from .views import touprnament_create, tournament_list, tournament_delete, tournament_update


urlpatterns = [
    path('create/', touprnament_create, name="create"),
    path('list/', tournament_list, name="list"),
    path('delete/<int:tournament_id>/', tournament_delete, name='tournament_delete'),
    path('update/<int:tournament_id>/', tournament_update, name='tournament_update')
]
