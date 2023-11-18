from django.urls import path
from .views import test_view, test_match


urlpatterns = [
	path('', test_view, name="test"),
    path('test/', test_match, name="test")
]
