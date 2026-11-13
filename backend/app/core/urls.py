"""
Configuration des URLs pour l'application core.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.core.views.auth_views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    logout_view,
    csrf_view,
    me_view,
    profile_view,
    public_profile_view,
    profile_photo_view,
    profile_banner_view,
    change_password_view,
    register_view,
    forgot_password_view,
    verify_reset_code_view,
    reset_password_view,
    check_permission_view,
    user_permissions_view,
    user_roles_view,
    CustomTokenVerifyView
)
from app.core.views.health_views import health_view
from app.core.views.user_viewset import UserViewSet
from app.core.views.role_viewset import RoleViewSet
from app.core.views.permission_viewset import PermissionViewSet

# Configuration du routeur pour les ViewSets
router = DefaultRouter(trailing_slash=False)
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'permissions', PermissionViewSet, basename='permission')


# URLs de l'application
urlpatterns = [
    # === SANTE (vérifications Docker et déploiement) ===
    path('health', health_view, name='health'),


    # === AUTHENTIFICATION JWT ===
    # Obtenir un token d'accès et de rafraîchissement
    path('auth/login', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Inscription publique (crée le compte + cookies de session)
    path('auth/register', register_view, name='register'),
    
    # Rafraîchir le token d'accès
    path('auth/token/refresh', CustomTokenRefreshView.as_view(), name='token_refresh'),
    
    # Vérifier la validité d'un token
    path('auth/token/verify', CustomTokenVerifyView.as_view(), name='token_verify'),
    
    # Cookie/jeton CSRF (à appeler avant la première requête modifiante)
    path('auth/csrf', csrf_view, name='csrf'),

    # Utilisateur connecté + permissions (lus en base)
    path('auth/me', me_view, name='me'),

    # Déconnexion (blacklist du token de rafraîchissement)
    path('auth/logout', logout_view, name='logout'),
    
    # === PROFIL UTILISATEUR ===
    # Obtenir le profil de l'utilisateur connecté
    path('auth/profile', profile_view, name='profile'),

    # Profil public d'un membre (mur Facebook-like)
    path('auth/public-profile/<int:user_id>', public_profile_view, name='public_profile'),
    # Alias conservé
    path('auth/profiles/<int:user_id>', public_profile_view, name='public_profile_alias'),

    # Photo de profil (upload / suppression)
    path('auth/profile/photo', profile_photo_view, name='profile_photo'),

    # Bannière de profil (upload / suppression)
    path('auth/profile/banner', profile_banner_view, name='profile_banner'),
    
    # Changer le mot de passe
    path('auth/change-password', change_password_view, name='change_password'),
    
    # === MOT DE PASSE OUBLIÉ (routes publiques) ===
    # Étape 1 : demande d'un code par e-mail
    path('auth/forgot-password', forgot_password_view, name='forgot_password'),

    # Étape 2 : vérification du code -> reset_token
    path('auth/verify-reset-code', verify_reset_code_view, name='verify_reset_code'),

    # Étape 3 : nouveau mot de passe avec le reset_token
    path('auth/reset-password', reset_password_view, name='reset_password'),

    # Vérifier une permission spécifique
    path('auth/check-permission', check_permission_view, name='check_permission'),
    
    # Obtenir toutes les permissions de l'utilisateur
    path('auth/permissions', user_permissions_view, name='user_permissions'),
    
    
    # Obtenir tous les rôles de l'utilisateur
    path('auth/roles', user_roles_view, name='user_roles'),
    
    # === API CRUD ===
    # Inclure toutes les routes des ViewSets
    path('v1/', include(router.urls)),
]

# URLs nommées pour faciliter les références
app_name = 'core'