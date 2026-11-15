"""
Serveur Socket.IO pour la messagerie privée (temps réel).

Auth : cookie JWT HttpOnly (même que l'API REST), repli auth.token Bearer.
Rooms : conversation:<id> — seuls les participants peuvent rejoindre.
"""
from __future__ import annotations

import asyncio
import logging
from http.cookies import SimpleCookie
from typing import Any, Optional

import socketio
from socketio.exceptions import ConnectionRefusedError as SocketConnectionRefused
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

logger = logging.getLogger(__name__)


def socketio_cors_origins() -> list[str]:
    """
    Origines autorisées pour Socket.IO (credentials) : CORS Django + FRONTEND_URL.
    '*' est exclu : il refuse les cookies.
    """
    origins: list[str] = []
    seen: set[str] = set()
    for raw in [*settings.CORS_ALLOWED_ORIGINS, settings.FRONTEND_URL]:
        origin = str(raw).strip().rstrip('/')
        if not origin or origin == '*' or origin in seen:
            continue
        seen.add(origin)
        origins.append(origin)
    return origins


sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=socketio_cors_origins(),
    logger=False,
    engineio_logger=False,
)

# Boucle asyncio du worker uvicorn (pour émettre depuis les vues DRF sync)
_main_loop: Optional[asyncio.AbstractEventLoop] = None


def bind_event_loop(loop: asyncio.AbstractEventLoop) -> None:
    global _main_loop
    _main_loop = loop


def conversation_room(conversation_id: int) -> str:
    return f'conversation:{int(conversation_id)}'


def _parse_cookies(environ: dict) -> dict[str, str]:
    raw = environ.get('HTTP_COOKIE')
    if not raw:
        return {}
    cookie = SimpleCookie()
    cookie.load(raw)
    return {key: morsel.value for key, morsel in cookie.items()}


def _refus(message: str) -> dict:
    """Accusé de réception d'échec d'un événement Socket.IO."""
    return {'ok': False, 'error': message}


def _conversation_id(data: Any) -> Optional[int]:
    """Identifiant de conversation d'un événement, ou None s'il est absent ou invalide."""
    value = data.get('conversation_id') if isinstance(data, dict) else None
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        return None
    text = str(value).strip()
    return int(text) if text.isdigit() else None


def _user_from_access_token(token: str):
    User = get_user_model()
    access = AccessToken(token)
    user_id = access.get('user_id')
    if user_id is None:
        return None
    return User.objects.filter(pk=user_id, is_active=True).first()


def authenticate_socket(environ: dict, auth: Any = None):
    """
    Résout l'utilisateur depuis le cookie access_token ou auth.token.

    Renvoie None si aucun jeton n'est fourni ; lève TokenError si le jeton est invalide ou expiré.
    """
    cookies = _parse_cookies(environ)
    token = cookies.get(settings.AUTH_COOKIE_ACCESS) or ''
    if not token and isinstance(auth, dict):
        token = str(auth.get('token') or '')
    if not token:
        return None
    return _user_from_access_token(token)


@sio.event
async def connect(sid, environ, auth=None):
    bind_event_loop(asyncio.get_running_loop())
    try:
        user = await sync_to_async(authenticate_socket, thread_sensitive=True)(
            environ, auth
        )
    except TokenError as error:
        logger.info('Socket.IO connect refusé (jeton invalide) sid=%s', sid)
        raise SocketConnectionRefused('Jeton invalide') from error
    if user is None:
        logger.info('Socket.IO connect refusé (non authentifié) sid=%s', sid)
        return False
    await sio.save_session(sid, {'user_id': user.id})
    await sio.enter_room(sid, f'user:{user.id}')
    logger.info('Socket.IO connecté user_id=%s sid=%s', user.id, sid)
    return True


@sio.event
async def disconnect(sid):
    logger.info('Socket.IO déconnecté sid=%s', sid)


@sio.event
async def join_conversation(sid, data):
    """Rejoint la room d'une conversation si le membre y participe."""
    session = await sio.get_session(sid)
    user_id = session.get('user_id')
    conversation_id = _conversation_id(data)
    if conversation_id is None:
        return _refus('conversation_id invalide')

    from app.communaute.services.conversation_service import ConversationService
    from django.contrib.auth import get_user_model
    from django.core.exceptions import ValidationError
    from django.http import Http404

    User = get_user_model()

    def _check():
        user = User.objects.filter(pk=user_id, is_active=True).first()
        if user is None:
            raise ValidationError('Utilisateur invalide')
        return ConversationService().get_for_user(conversation_id, user)

    try:
        await sync_to_async(_check, thread_sensitive=True)()
    except Http404:
        return _refus('Conversation introuvable')
    except ValidationError as e:
        return _refus(str(e))

    room = conversation_room(conversation_id)
    await sio.enter_room(sid, room)
    return {'ok': True, 'room': room}


@sio.event
async def leave_conversation(sid, data):
    conversation_id = _conversation_id(data)
    if conversation_id is None:
        return _refus('conversation_id invalide')
    await sio.leave_room(sid, conversation_room(conversation_id))
    return {'ok': True}


async def _emit_message_new(conversation_id: int, payload: dict) -> None:
    await sio.emit(
        'message:new',
        payload,
        room=conversation_room(conversation_id),
    )


def emit_message_new(conversation_id: int, payload: dict) -> None:
    """
    Émet un nouveau message vers la room (appelable depuis une vue DRF sync).
    Nécessite uvicorn (boucle asyncio active).
    """
    coro = _emit_message_new(conversation_id, payload)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # Appel depuis un thread synchrone (vue DRF) : on passe par la boucle du worker.
        _schedule_on_main_loop(coro)
        return
    loop.create_task(coro)


def _schedule_on_main_loop(coro) -> None:
    if _main_loop is not None and _main_loop.is_running():
        asyncio.run_coroutine_threadsafe(coro, _main_loop)
        return
    coro.close()  # évite l'avertissement « coroutine never awaited »
    logger.warning(
        "Socket.IO : impossible d'émettre message:new (pas de boucle asyncio). "
        'Lance le backend avec uvicorn, pas runserver.'
    )
