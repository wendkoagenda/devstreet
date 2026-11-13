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
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

logger = logging.getLogger(__name__)

sio = socketio.AsyncServer(
    async_mode='asgi',
    # Origines du front Vite (proxy same-host) ; '*' refuse les credentials
    cors_allowed_origins=[
        'http://localhost:5173',
        'http://127.0.0.1:5173',
    ],
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
    raw = environ.get('HTTP_COOKIE') or ''
    cookie = SimpleCookie()
    cookie.load(raw)
    return {key: morsel.value for key, morsel in cookie.items()}


def _user_from_access_token(token: str):
    User = get_user_model()
    access = AccessToken(token)
    user_id = access.get('user_id')
    if user_id is None:
        return None
    return User.objects.filter(pk=user_id, is_active=True).first()


def authenticate_socket(environ: dict, auth: Any = None):
    """Résout l'utilisateur depuis le cookie access_token ou auth.token."""
    cookies = _parse_cookies(environ)
    token = cookies.get(settings.AUTH_COOKIE_ACCESS) or ''
    if not token and isinstance(auth, dict):
        token = str(auth.get('token') or '')
    if not token:
        return None
    try:
        return _user_from_access_token(token)
    except Exception:
        logger.info('Socket.IO : jeton d\'accès invalide')
        return None


@sio.event
async def connect(sid, environ, auth=None):
    bind_event_loop(asyncio.get_running_loop())
    user = await sync_to_async(authenticate_socket, thread_sensitive=True)(
        environ, auth
    )
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
    try:
        conversation_id = int((data or {}).get('conversation_id'))
    except (TypeError, ValueError):
        return {'ok': False, 'error': 'conversation_id invalide'}

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
        return {'ok': False, 'error': 'Conversation introuvable'}
    except ValidationError as e:
        return {'ok': False, 'error': str(e)}

    room = conversation_room(conversation_id)
    await sio.enter_room(sid, room)
    return {'ok': True, 'room': room}


@sio.event
async def leave_conversation(sid, data):
    try:
        conversation_id = int((data or {}).get('conversation_id'))
    except (TypeError, ValueError):
        return {'ok': False, 'error': 'conversation_id invalide'}
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
        loop.create_task(coro)
        return
    except RuntimeError:
        pass

    if _main_loop is not None and _main_loop.is_running():
        asyncio.run_coroutine_threadsafe(coro, _main_loop)
        return

    logger.warning(
        'Socket.IO : impossible d\'émettre message:new (pas de boucle asyncio). '
        'Lance le backend avec uvicorn, pas runserver.'
    )
