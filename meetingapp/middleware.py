"""
JWT auth middleware for Django Channels WebSocket connections.

Browsers cannot set Authorization headers on WebSocket connections.
Standard workaround: pass the JWT as a query param → ?token=<access_token>

Security note: query params appear in server access logs.
For production, consider a one-time nonce approach:
  1. Client calls POST /api/ws-ticket/ → gets a 30-second nonce
  2. Client passes nonce in WS query param
  3. Consumer validates nonce and discards it
This MVP uses direct JWT in query param for simplicity.
"""
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        scope["user"] = await self._get_user(scope)
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def _get_user(self, scope):
        # Lazy imports: Django app registry must be ready before importing models.
        # These run inside a sync thread via database_sync_to_async, after setup().
        from django.contrib.auth.models import AnonymousUser
        from django.contrib.auth import get_user_model
        from rest_framework_simplejwt.tokens import AccessToken

        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token = params.get("token", [None])[0]
        if not token:
            return AnonymousUser()
        try:
            User = get_user_model()
            validated = AccessToken(token)
            return User.objects.get(id=validated["user_id"])
        except Exception:
            return AnonymousUser()


def JWTAuthMiddlewareStack(inner):
    return JWTAuthMiddleware(inner)
