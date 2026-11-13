"""
ASGI config — Django HTTP + Socket.IO (messagerie temps réel).

Lancer en local :
  uvicorn config.asgi:application --reload --host 127.0.0.1 --port 8000

``manage.py runserver`` ne gère pas correctement les WebSockets Socket.IO.
"""
import asyncio
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

import socketio  # noqa: E402
from app.communaute.socketio_app import bind_event_loop, sio  # noqa: E402

_socket_app = socketio.ASGIApp(
    sio,
    other_asgi_app=django_asgi_app,
    socketio_path='socket.io',
)


class _BindLoopASGI:
    """Mémorise la boucle uvicorn pour les emits depuis les vues DRF sync."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        bind_event_loop(asyncio.get_running_loop())
        await self.app(scope, receive, send)


application = _BindLoopASGI(_socket_app)
