from django.urls import path
from .views import *


urlpatterns = [
	# Friend
    path('user/<int:pk>/addfriend/', user_add_friend, name='user_addfriend'),
	path('user/<int:pk>/removefriend/', user_remove_friend, name='user_removefriend'),
	# path('user/<int:pk>/friendlist/', user_friend_list, name='user_friendlist'),
]