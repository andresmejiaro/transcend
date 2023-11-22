from django.urls import path, include
from .views import test_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
	path('', test_view, name="test"),
    path('user/', include('api.userauth.urls')),
    path('tournament/', include('api.tournament.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)