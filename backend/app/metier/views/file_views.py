"""Lecture authentifiée des fichiers stockés (``GET /api/v1/files/<chemin>``).

Avec ``USE_S3=True``, le bucket est privé et n'a aucune URL publique : l'application lit l'objet avec ses clés
applicatives et le renvoie en flux, seulement à un utilisateur connecté (cookie JWT). Le chemin est celui enregistré
en base (ex. ``forum_images/photo.png``). Fonctionne aussi avec le disque local.
"""
import logging
import mimetypes
import posixpath
import re
from typing import Optional, Tuple

from django.http import Http404, HttpResponse, StreamingHttpResponse
from rest_framework.negotiation import BaseContentNegotiation
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from app.metier.services.storage_service import get_storage_service

logger = logging.getLogger(__name__)

_CHUNK_SIZE = 64 * 1024
_RANGE_RE = re.compile(r'^bytes=(\d*)-(\d*)$')
# Types affichés dans le navigateur ; tout le reste est téléchargé (jamais interprété par la page).
_INLINE_PREFIXES = ('image/', 'video/', 'audio/')
_INLINE_TYPES = ('application/pdf',)
_CACHE_CONTROL = 'private, max-age=86400'  # jamais de cache partagé : le fichier est réservé aux utilisateurs connectés


class FileReadThrottle(UserRateThrottle):
    """Une page affiche beaucoup d'images : limite dédiée, plus large que la limite générale de l'API."""
    scope = 'files'


class AnyAcceptNegotiation(BaseContentNegotiation):
    """
    Un ``<img>`` envoie ``Accept: image/*`` : avec la négociation DRF par défaut (rendus JSON), la requête serait refusée
    en 406. La réponse est un fichier, pas du JSON : l'en-tête Accept est ignoré.
    """

    def select_parser(self, request, parsers):
        return parsers[0]

    def select_renderer(self, request, renderers, format_suffix=None):
        return renderers[0], renderers[0].media_type


def normalize_file_path(raw_path: str) -> Optional[str]:
    """Chemin relatif sûr, ou None s'il sort du stockage (``..``, chemin absolu, antislash, octet nul)."""
    if not raw_path or '\\' in raw_path or '\x00' in raw_path:
        return None
    normalized = posixpath.normpath(raw_path)
    if normalized.startswith('/') or normalized == '.' or normalized == '..' or normalized.startswith('../'):
        return None
    return normalized


def parse_range(header: str, size: int) -> Optional[Tuple[int, int]]:
    """
    Lit ``Range: bytes=a-b`` (une seule plage). Retourne (début, fin incluse), ou None si la plage est
    illisible ou hors du fichier.
    """
    match = _RANGE_RE.match(header.strip())
    if not match or size <= 0:
        return None
    first, last = match.groups()
    if first == '' and last == '':
        return None
    if first == '':  # « les N derniers octets »
        length = int(last)
        if length == 0:
            return None
        return max(size - length, 0), size - 1
    start = int(first)
    end = int(last) if last != '' else size - 1
    if start >= size or end < start:
        return None
    return start, min(end, size - 1)


def _iterate(file_obj, start: int, length: int):
    """Lit ``length`` octets à partir de ``start`` par blocs, puis ferme le fichier."""
    try:
        file_obj.seek(start)
        remaining = length
        while remaining > 0:
            chunk = file_obj.read(min(_CHUNK_SIZE, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
            yield chunk
    finally:
        file_obj.close()


class StoredFileView(APIView):
    """Renvoie un fichier stocké, à un utilisateur connecté uniquement."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [FileReadThrottle]
    content_negotiation_class = AnyAcceptNegotiation

    def get(self, request, file_path: str):
        name = normalize_file_path(file_path)
        if name is None:
            raise Http404

        storage = get_storage_service()
        try:
            if not storage.exists(name):
                raise Http404
            size = storage.size(name)
            file_obj = storage.open(name, 'rb')
        except Http404:
            raise
        except Exception:
            logger.exception("Lecture impossible du fichier %s", name)
            return HttpResponse(status=502)

        content_type = mimetypes.guess_type(name)[0] or 'application/octet-stream'
        start, length, status_code = 0, size, 200
        range_header = request.headers.get('Range')
        content_range = None
        if range_header:
            byte_range = parse_range(range_header, size)
            if byte_range is None:
                file_obj.close()
                response = HttpResponse(status=416)
                response['Content-Range'] = f'bytes */{size}'
                return response
            start, end = byte_range
            length = end - start + 1
            status_code = 206
            content_range = f'bytes {start}-{end}/{size}'

        response = StreamingHttpResponse(_iterate(file_obj, start, length), status=status_code, content_type=content_type)
        response['Content-Length'] = str(length)
        response['Accept-Ranges'] = 'bytes'
        if content_range:
            response['Content-Range'] = content_range
        response['Cache-Control'] = _CACHE_CONTROL
        response['X-Content-Type-Options'] = 'nosniff'
        inline = content_type.startswith(_INLINE_PREFIXES) or content_type in _INLINE_TYPES
        filename = posixpath.basename(name).replace('"', '')
        response['Content-Disposition'] = f'{"inline" if inline else "attachment"}; filename="{filename}"'
        return response
