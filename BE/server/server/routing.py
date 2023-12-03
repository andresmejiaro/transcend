import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import path, re_path
from pong_app.consumers import PongConsumer
from pong_app.routing import websocket_pong_urlpatterns
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django.setup()
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_pong_urlpatterns,
            )
    ),
})