from django.urls import path, include
from .views import test_view


urlpatterns = [
	path('test/', test_view, name="test"),
    path('', include('api.userauth.urls')),
    path('', include('api.tournament.urls')),
]
