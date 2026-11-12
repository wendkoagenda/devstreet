"""
Vues d'authentification JWT pour l'application core.
"""
import logging

from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings
from django.middleware.csrf import get_token
from app.core.cookies import clear_auth_cookies, set_auth_cookies
from app.core.services import audit_service, login_lockout
from app.core.services.audit_service import Actions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.core.serializers import (
    UserSerializer,
    PasswordChangeSerializer,
    UserLoginSerializer,
    ForgotPasswordSerializer,
    VerifyResetCodeSerializer,
    ResetPasswordSerializer,
)
from app.core.services.forgot_password_service import (
    ForgotPasswordService,
    PasswordResetError,
    GENERIC_REQUEST_MESSAGE,
    CODE_VERIFIED_MESSAGE,
    RESET_SUCCESS_MESSAGE,
)
from app.core.throttles import (
    CsrfThrottle,
    LoginThrottle,
    LogoutThrottle,
    TokenRefreshThrottle,
    TokenVerifyThrottle,
    PasswordResetRequestThrottle,
    PasswordResetVerifyThrottle,
    PasswordResetConfirmThrottle,
)

logger = logging.getLogger(__name__)

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Sérialiseur personnalisé pour l'obtention de tokens JWT avec informations utilisateur enrichies.
    """
    
    @classmethod
    def get_token(cls, user):
        """
        Génère un token JWT avec des informations utilisateur personnalisées.
        
        Args:
            user: L'utilisateur pour lequel générer le token
            
        Returns:
            Token JWT avec informations enrichies
        """
        token = super().get_token(user)
        
        # Ajouter des informations personnalisées au token
        token['user_id'] = user.id
        token['email'] = user.email
        token['full_name'] = user.full_name
        # Les rôles et permissions ne sont PAS dans le jeton : ils changent sans reconnexion et alourdiraient
        # le cookie. Le front les relit en base via GET /api/auth/me.
        
        return token

    def validate(self, attrs):
        """
        Valide les données et retourne les tokens avec les informations utilisateur.
        """
        data = super().validate(attrs)
        
        # Utilise le nouveau serializer pour limiter les infos renvoyées
        user_serializer = UserLoginSerializer(self.user)
        data['user'] = user_serializer.data
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vue personnalisée pour l'obtention de tokens JWT.
    """
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [LoginThrottle]

    @swagger_auto_schema(
        operation_description="Obtenir un token JWT d'accès et de rafraîchissement",
        responses={
            200: openapi.Response(
                description="Tokens générés avec succès",
                examples={
                    "application/json": {
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "username": "user",
                            "full_name": "John Doe",
                            "roles": ["admin"]
                        }
                    }
                }
            ),
            401: "Identifiants invalides"
        },
        tags=['Auth']
    )
    def post(self, request, *args, **kwargs):
        """
        Authentifie l'utilisateur : les jetons sont posés dans des cookies HttpOnly, le corps ne contient que l'utilisateur.
        """
        email = request.data.get('email')
        key = audit_service.account_key(email)
        if login_lockout.is_locked(key):
            # Même réponse que le compte existe ou non ; la fenêtre se vide d'elle-même
            locked = Response({'detail': 'Trop de tentatives de connexion. Réessayez plus tard.'},
                              status=status.HTTP_429_TOO_MANY_REQUESTS)
            locked['Retry-After'] = str(settings.LOGIN_LOCKOUT_MINUTES * 60)
            return locked

        try:
            response = super().post(request, *args, **kwargs)
        except AuthenticationFailed:
            # Identifiants refusés : l'échec est journalisé (il alimente le verrouillage), puis la réponse 401 suit
            known = User.objects.filter(email__iexact=email.strip()).first() if isinstance(email, str) and email.strip() else None
            audit_service.record(Actions.LOGIN_FAILED, target=known, subject=key, request=request)
            raise
        if response.status_code == status.HTTP_200_OK:
            user = User.objects.filter(pk=response.data['user']['id']).first()
            audit_service.record(Actions.LOGIN_SUCCESS, actor=user, target=user, subject=key, request=request)
            set_auth_cookies(response, response.data.get('access'), response.data.get('refresh'))
            response.data = {'user': response.data.get('user')}
        return response


class CustomTokenRefreshView(TokenRefreshView):
    """
    Vue personnalisée pour le rafraîchissement de tokens JWT.
    """
    throttle_classes = [TokenRefreshThrottle]
    
    @swagger_auto_schema(
        operation_description="Rafraîchir un token JWT d'accès",
        responses={
            200: openapi.Response(
                description="Token rafraîchi avec succès",
                examples={
                    "application/json": {
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                    }
                }
            ),
            401: "Token de rafraîchissement invalide"
        },
        tags=['Auth']
    )
    def post(self, request, *args, **kwargs):
        """
        Rafraîchit les jetons. Le refresh token vient du cookie (SPA) ou du corps (scripts) ;
        les nouveaux jetons sont posés en cookies (rotation + liste noire de l'ancien refresh).
        """
        from_body = request.data.get('refresh')
        refresh = from_body or request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)
        if not refresh:
            return Response({'detail': 'Token de rafraîchissement manquant'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(data={'refresh': refresh})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as error:
            raise InvalidToken(error.args[0])

        data = serializer.validated_data
        # Un client qui fournit lui-même le refresh dans le corps (script) reçoit aussi les jetons dans la réponse
        response = Response(dict(data) if from_body else {'detail': 'Session renouvelée'}, status=status.HTTP_200_OK)
        return set_auth_cookies(response, data.get('access'), data.get('refresh'))


class CustomTokenVerifyView(TokenVerifyView):
    throttle_classes = [TokenVerifyThrottle]

    @swagger_auto_schema(
        operation_description="Vérifier la validité d'un token JWT",
        tags=['Auth'],
        responses={200: "Token valide", 401: "Token invalide"}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@swagger_auto_schema(
    method='post',
    operation_description="Déconnecter l'utilisateur : invalide le refresh token et supprime les cookies",
    responses={200: "Déconnexion réussie"},
    tags=['Auth']
)
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([LogoutThrottle])
def logout_view(request):
    """
    Déconnecte l'utilisateur. Idempotent : les cookies sont toujours supprimés, même si le token
    est déjà expiré ou invalide (on ne laisse jamais un utilisateur « coincé » connecté).
    """
    refresh_token = request.data.get('refresh') or request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)
    if refresh_token:
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError as error:
            # Déjà expiré, invalide ou en liste noire : la déconnexion continue (les cookies sont supprimés)
            logger.info("Déconnexion : refresh token non blacklisté (%s)", error)
    response = Response({'message': 'Déconnexion réussie'}, status=status.HTTP_200_OK)
    return clear_auth_cookies(response)


@swagger_auto_schema(
    method='get',
    operation_description="Pose le cookie CSRF et retourne le jeton (à renvoyer dans l'en-tête X-CSRFToken)",
    responses={200: openapi.Response(description="Jeton CSRF", examples={"application/json": {"csrfToken": "..."}})},
    tags=['Auth']
)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([CsrfThrottle])
def csrf_view(request):
    """Pose le cookie `csrftoken` et retourne le jeton (utile quand le front ne peut pas lire le cookie)."""
    return Response({'csrfToken': get_token(request)}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Utilisateur connecté, avec ses rôles et permissions actuels (lus en base)",
    responses={200: "Utilisateur et permissions", 401: "Non authentifié"},
    tags=['Auth']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """Identité, rôles et permissions de l'utilisateur, relus en base (donc à jour sans reconnexion)."""
    data = UserLoginSerializer(request.user).data
    return Response({'user': data, 'permissions': request.user.get_all_permissions()}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Obtenir les informations du profil utilisateur actuel",
    responses={
        200: UserSerializer,
        401: "Non authentifié"
    },
    tags=['Auth']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Retourne les informations du profil de l'utilisateur authentifié.
    
    Args:
        request: La requête HTTP
        
    Returns:
        Response: Les informations du profil utilisateur
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Changer le mot de passe de l'utilisateur actuel",
    request_body=PasswordChangeSerializer,
    responses={
        200: "Mot de passe changé avec succès",
        400: "Données invalides",
        401: "Non authentifié"
    },
    tags=['Auth']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    Permet à l'utilisateur authentifié de changer son mot de passe.
    
    Args:
        request: La requête HTTP contenant l'ancien et le nouveau mot de passe
        
    Returns:
        Response: Confirmation du changement de mot de passe
    """
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        # Changer le mot de passe
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        audit_service.record(Actions.PASSWORD_CHANGED, actor=user, target=user, request=request)

        return Response(
            {'message': 'Mot de passe changé avec succès'},
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    operation_description="Vérifier si l'utilisateur a une permission spécifique",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'permission_code': openapi.Schema(type=openapi.TYPE_STRING, description='Code de la permission à vérifier')
        },
        required=['permission_code']
    ),
    responses={
        200: openapi.Response(
            description="Résultat de la vérification",
            examples={
                "application/json": {
                    "permission_code": "users.view",
                    "has_permission": True
                }
            }
        ),
        400: "Code de permission requis",
        401: "Non authentifié"
    },
    tags=['Auth']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_permission_view(request):
    """
    Vérifie si l'utilisateur authentifié a une permission spécifique.
    
    Args:
        request: La requête HTTP contenant le code de permission
        
    Returns:
        Response: Résultat de la vérification de permission
    """
    permission_code = request.data.get('permission_code')
    
    if not permission_code:
        return Response(
            {'error': 'Code de permission requis'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    has_permission = request.user.has_permission(permission_code)
    
    return Response({
        'permission_code': permission_code,
        'has_permission': has_permission
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Obtenir toutes les permissions de l'utilisateur actuel",
    responses={
        200: openapi.Response(
            description="Liste des permissions",
            examples={
                "application/json": {
                    "permissions": ["users.view", "users.create", "roles.view"]
                }
            }
        ),
        401: "Non authentifié"
    },
    tags=['Auth']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_permissions_view(request):
    """
    Retourne toutes les permissions de l'utilisateur authentifié.
    
    Args:
        request: La requête HTTP
        
    Returns:
        Response: Liste des permissions de l'utilisateur
    """
    permissions = request.user.get_all_permissions()
    
    return Response({
        'permissions': permissions
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Obtenir tous les rôles de l'utilisateur actuel",
    responses={
        200: openapi.Response(
            description="Liste des rôles",
            examples={
                "application/json": {
                    "roles": ["admin", "editor"]
                }
            }
        ),
        401: "Non authentifié"
    },
    tags=['Auth']
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_roles_view(request):
    """
    Retourne tous les rôles de l'utilisateur authentifié.
    
    Args:
        request: La requête HTTP
        
    Returns:
        Response: Liste des rôles de l'utilisateur
    """
    roles = request.user.get_roles()
    
    return Response({
        'roles': roles
    }, status=status.HTTP_200_OK)


# === MOT DE PASSE OUBLIÉ (challenge e-mail) ===
# Routes publiques : l'en-tête Authorization est ignoré (un ancien token expiré ne doit pas provoquer de 401).

def _first_error_message(errors) -> str:
    """Extrait un message lisible des erreurs d'un serializer (format { "error": "..." })."""
    for value in errors.values():
        if isinstance(value, (list, tuple)) and value:
            return str(value[0])
        if isinstance(value, dict):
            return _first_error_message(value)
        return str(value)
    return "Données invalides."


@swagger_auto_schema(
    method='post',
    operation_description="Étape 1 : demander un code de réinitialisation par e-mail (réponse générique)",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={'email': openapi.Schema(type=openapi.TYPE_STRING, description="Adresse e-mail du compte")},
        required=['email']
    ),
    responses={200: "Message générique (le compte existe ou non)", 400: "E-mail invalide", 429: "Trop de demandes"},
    tags=['Auth']
)
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([PasswordResetRequestThrottle])
def forgot_password_view(request):
    """
    Demande un code de réinitialisation. La réponse est identique que le compte existe ou non.
    """
    serializer = ForgotPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': _first_error_message(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)

    ForgotPasswordService().request_password_reset(serializer.validated_data['email'])
    return Response({'message': GENERIC_REQUEST_MESSAGE}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Étape 2 : vérifier le code reçu par e-mail et obtenir un reset_token à usage unique",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING),
            'code': openapi.Schema(type=openapi.TYPE_STRING, description="Code à 6 chiffres"),
        },
        required=['email', 'code']
    ),
    responses={200: "Code valide : reset_token renvoyé", 400: "Code invalide ou expiré", 429: "Trop de tentatives"},
    tags=['Auth']
)
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([PasswordResetVerifyThrottle])
def verify_reset_code_view(request):
    """
    Vérifie le code et retourne un reset_token (affiché une seule fois).
    """
    serializer = VerifyResetCodeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': _first_error_message(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)

    try:
        reset_token = ForgotPasswordService().verify_reset_code(
            serializer.validated_data['email'],
            serializer.validated_data['code'],
        )
    except PasswordResetError as error:
        return Response({'error': error.message}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': CODE_VERIFIED_MESSAGE, 'reset_token': reset_token}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Étape 3 : définir le nouveau mot de passe avec le reset_token",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'reset_token': openapi.Schema(type=openapi.TYPE_STRING),
            'new_password': openapi.Schema(type=openapi.TYPE_STRING),
            'new_password_confirm': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['reset_token', 'new_password', 'new_password_confirm']
    ),
    responses={200: "Mot de passe mis à jour", 400: "Token invalide/expiré ou mot de passe refusé", 429: "Trop de demandes"},
    tags=['Auth']
)
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([PasswordResetConfirmThrottle])
def reset_password_view(request):
    """
    Définit le nouveau mot de passe, puis invalide les sessions (refresh tokens) existantes.
    """
    serializer = ResetPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': _first_error_message(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = ForgotPasswordService().confirm_password_reset(
            serializer.validated_data['reset_token'],
            serializer.validated_data['new_password'],
        )
    except PasswordResetError as error:
        return Response({'error': error.message}, status=status.HTTP_400_BAD_REQUEST)

    audit_service.record(Actions.PASSWORD_RESET, target=user, request=request)
    return Response({'message': RESET_SUCCESS_MESSAGE}, status=status.HTTP_200_OK)
