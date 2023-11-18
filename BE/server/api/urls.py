from django.urls import path, include
from .views import test_view


urlpatterns = [
	path('', test_view, name="test"),
    path('user/', include('api.userauth.urls')),
    path('tournament/', include('api.tournament.urls')),
]
