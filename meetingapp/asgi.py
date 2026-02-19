"""
ASGI entry point.
Daphne routes HTTP → Django, WebSocket → Channels.
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meetingapp.settings")
# Must call setup() before any import that touches models or app registry.
django.setup()

from django.core.asgi import get_asgi_application  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.security.websocket import AllowedHostsOriginValidator  # noqa: E402
from meetingapp.middleware import JWTAuthMiddlewareStack  # noqa: E402
import meetingapp.routing  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(
            JWTAuthMiddlewareStack(
                URLRouter(meetingapp.routing.websocket_urlpatterns)
            )
        ),
    }
)
