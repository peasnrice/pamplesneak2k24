"""
ASGI config for pamplesneak project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pamplesneak.settings")
django.setup()  # Ensure Django is fully set up

# Import gameroom.routing after Django setup
import gameroom.routing as gameroom_routing

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(gameroom_routing.websocket_urlpatterns)
        ),
    }
)
