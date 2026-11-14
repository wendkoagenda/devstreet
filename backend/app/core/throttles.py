"""
Limitation de débit des routes publiques d'authentification (par adresse IP) :
connexion, rafraîchissement et vérification du token, déconnexion, CSRF et réinitialisation de mot de passe.
Les autres routes sont couvertes par la limite par défaut (DEFAULT_THROTTLE_CLASSES de settings.py).

Les taux sont des constantes de settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] (config/settings.py).
"""
from rest_framework.throttling import AnonRateThrottle


class PasswordResetRequestThrottle(AnonRateThrottle):
    """Étape 1 : demande de code (limite l'envoi massif d'e-mails)."""
    scope = 'password_reset_request'


class PasswordResetVerifyThrottle(AnonRateThrottle):
    """Étape 2 : vérification du code."""
    scope = 'password_reset_verify'


class PasswordResetConfirmThrottle(AnonRateThrottle):
    """Étape 3 : définition du nouveau mot de passe."""
    scope = 'password_reset_confirm'


class LoginThrottle(AnonRateThrottle):
    """Connexion : freine les essais de mots de passe en masse."""
    scope = 'login'


class RegisterThrottle(AnonRateThrottle):
    """Inscription publique : limite la création de comptes en masse."""
    scope = 'register'


class TokenRefreshThrottle(AnonRateThrottle):
    """Rafraîchissement du token d'accès."""
    scope = 'token_refresh'


class TokenVerifyThrottle(AnonRateThrottle):
    """Vérification d'un jeton."""
    scope = 'token_verify'


class LogoutThrottle(AnonRateThrottle):
    """Déconnexion."""
    scope = 'logout'


class CsrfThrottle(AnonRateThrottle):
    """Demande du jeton CSRF."""
    scope = 'csrf'


class HealthThrottle(AnonRateThrottle):
    """Route de santé : chaque appel interroge la base, donc la fréquence est bornée."""
    scope = 'health'


class OAuthProvidersThrottle(AnonRateThrottle):
    """Liste des providers OAuth configurés (route publique lue par la page de connexion)."""
    scope = 'oauth_providers'


class OAuthStartThrottle(AnonRateThrottle):
    """Démarrage du flux OAuth (redirection IdP)."""
    scope = 'oauth_start'


class OAuthCallbackThrottle(AnonRateThrottle):
    """Callback OAuth (échange de code)."""
    scope = 'oauth_callback'
