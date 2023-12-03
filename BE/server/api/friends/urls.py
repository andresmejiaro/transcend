from django.urls import path
from .views import *

urlpatterns = [
	# Friend
    path('user/<int:pk>/addfriend/', user_add_friend, name='user_addfriend'),
	path('user/<int:pk>/removefriend/', user_remove_friend, name='user_removefriend'),
	path('user/<int:pk>/friendlist/', user_friends_list, name='user_friendlist'),
    path('user/<int:pk>/blockuser/', user_block_user, name='user_friendrequests'),
    path('user/<int:pk>/unblockuser/', user_unblock_user, name='user_friendrequests'),
]