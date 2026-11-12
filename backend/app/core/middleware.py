"""
Middlewares personnalisés : limite de taille des requêtes et authentification JWT.
"""
import re

from django.conf import settings
from django.http import JsonResponse

MULTIPART_OVERHEAD_MB = 1


class RequestSizeLimitMiddleware:
    """
    Refuse une requête dont l'en-tête Content-Length dépasse le plafond de téléversement (UPLOAD_MAX_SIZE_MB + 1 Mo
    de multipart), avant que Django ne la lise : un fichier énorme ne remplit ni la mémoire ni le disque.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        length = request.META.get('CONTENT_LENGTH', '')
        if length and not length.isdigit():
            return JsonResponse({'error': 'En-tête Content-Length invalide'}, status=400)
        limit = (settings.UPLOAD_MAX_SIZE_MB + MULTIPART_OVERHEAD_MB) * 1024 * 1024
        if length and int(length) > limit:
            return JsonResponse({'error': f'Requête trop volumineuse (maximum {settings.UPLOAD_MAX_SIZE_MB} Mo)'}, status=413)
        return self.get_response(request)


class JWTAuthenticationMiddleware:
    """
    Middleware pour gérer automatiquement le préfixe Bearer pour les tokens JWT.

    Ce middleware intercepte les requêtes et ajoute automatiquement le préfixe 'Bearer '
    aux tokens JWT qui n'en ont pas, pour assurer la compatibilité avec Swagger.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Vérifier si l'en-tête Authorization existe
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if auth_header:
            # Pattern pour détecter un token JWT (3 parties séparées par des points)
            jwt_pattern = r'^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$'

            # Si c'est un token JWT sans préfixe Bearer, l'ajouter
            if re.match(jwt_pattern, auth_header.strip()):
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {auth_header}'

        response = self.get_response(request)
        return response