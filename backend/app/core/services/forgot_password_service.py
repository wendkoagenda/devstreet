"""
Service du flux « mot de passe oublié » basé sur un challenge e-mail.

Trois étapes :
1. request_password_reset : envoi d'un code à 6 chiffres par e-mail.
2. verify_reset_code      : vérification du code, émission d'un reset_token à usage unique.
3. confirm_password_reset : définition du nouveau mot de passe avec ce token.

Le mot de passe n'est modifié qu'à l'étape 3. Le code et le token ne sont jamais
stockés ni journalisés en clair : seules leurs empreintes HMAC-SHA256 (clé = SECRET_KEY)
sont conservées, et comparées en temps constant.
"""
import hashlib
import hmac
import logging
import secrets
from datetime import timedelta
from typing import Optional
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from app.core.interfaces.password_reset_challenge_repository_interface import (
    PasswordResetChallengeRepositoryInterface,
)
from app.core.interfaces.user_repository_interface import UserRepositoryInterface
from app.core.repositories.password_reset_challenge_repository import PasswordResetChallengeRepository
from app.core.repositories.user_repository import UserRepository
from app.core.services.email_service import EmailService

logger = logging.getLogger(__name__)

# === Constantes métier (à aligner avec le gabarit e-mail si elles changent) ===
CODE_LENGTH = 6                  # chiffres uniquement
CODE_TTL_MINUTES = 15            # durée de vie du code
MAX_ATTEMPTS = 5                 # essais max avant de devoir redemander un code
RESET_TOKEN_TTL_MINUTES = 10     # durée de vie du reset_token après vérification du code
RESEND_COOLDOWN_SECONDS = 60     # délai minimal entre deux demandes pour un même compte

# === Messages ===
# Message identique que le compte existe ou non (pas d'énumération d'adresses e-mail).
GENERIC_REQUEST_MESSAGE = (
    "Si un compte est associé à cette adresse, un code de vérification vient d'être envoyé."
)
# Un seul message pour tous les échecs de l'étape 2 (compte inconnu, code faux, expiré, trop d'essais),
# afin de ne rien révéler sur l'existence du compte.
INVALID_CODE_MESSAGE = "Code invalide ou expiré. Redemandez un code si nécessaire."
INVALID_TOKEN_MESSAGE = "Votre session de réinitialisation est invalide ou expirée. Recommencez la procédure."
RESET_SUCCESS_MESSAGE = "Votre mot de passe a été mis à jour. Vous pouvez vous connecter."
CODE_VERIFIED_MESSAGE = "Code vérifié. Vous pouvez choisir un nouveau mot de passe."


class PasswordResetError(Exception):
    """Erreur métier du flux de réinitialisation (renvoyée en HTTP 400)."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ForgotPasswordService:
    """
    Orchestration du flux « mot de passe oublié ».
    """

    def __init__(
        self,
        user_repository: Optional[UserRepositoryInterface] = None,
        challenge_repository: Optional[PasswordResetChallengeRepositoryInterface] = None,
        email_service: Optional[EmailService] = None,
    ):
        self.user_repository = user_repository or UserRepository()
        self.challenge_repository = challenge_repository or PasswordResetChallengeRepository()
        self.email_service = email_service or EmailService()

    # ------------------------------------------------------------------ utilitaires
    @staticmethod
    def _digest(purpose: str, value: str) -> str:
        """Empreinte HMAC-SHA256 d'un secret (le `purpose` évite toute réutilisation entre usages)."""
        return hmac.new(
            settings.SECRET_KEY.encode('utf-8'),
            f"{purpose}:{value}".encode('utf-8'),
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    def _normalize_email(email: str) -> str:
        return (email or '').lower().strip()

    @staticmethod
    def _generate_code() -> str:
        return ''.join(secrets.choice('0123456789') for _ in range(CODE_LENGTH))

    # ------------------------------------------------------------------ étape 1
    def request_password_reset(self, email: str) -> None:
        """
        Envoie un code de vérification si un compte actif correspond à l'adresse.

        Ne signale jamais si le compte existe : compte inconnu ou inactif, demande trop
        rapprochée ou échec d'envoi aboutissent au même retour silencieux.
        """
        user = self.user_repository.get_active_by_email(self._normalize_email(email))
        if user is None:
            return

        now = timezone.now()
        last_created_at = self.challenge_repository.get_latest_created_at(user)
        if last_created_at and (now - last_created_at).total_seconds() < RESEND_COOLDOWN_SECONDS:
            return

        code = self._generate_code()
        try:
            with transaction.atomic():
                # Les codes précédents ne sont plus utilisables
                self.challenge_repository.invalidate_open_for_user(user, now)
                self.challenge_repository.create(
                    user=user,
                    code_hash=self._digest(f"code:{user.pk}", code),
                    expires_at=now + timedelta(minutes=CODE_TTL_MINUTES),
                )
                self.email_service.send_templated(
                    to_email=user.email,
                    subject="Votre code de réinitialisation de mot de passe",
                    template_name='password_reset',
                    context={
                        'first_name': user.first_name or user.username,
                        'reset_code': code,
                        'code_ttl_minutes': CODE_TTL_MINUTES,
                        'login_url': f"{settings.FRONTEND_URL}/login",
                    },
                )
        except Exception:
            # La transaction est annulée : le challenge n'existe pas et les précédents restent valides.
            # Aucune erreur n'est renvoyée au client (elle révélerait que le compte existe).
            logger.error("Échec de l'envoi du code de réinitialisation (user_id=%s)", user.pk, exc_info=True)

    # ------------------------------------------------------------------ étape 2
    def verify_reset_code(self, email: str, code: str) -> str:
        """
        Vérifie le code et retourne un reset_token à usage unique (en clair, une seule fois).

        Raises:
            PasswordResetError: code invalide, expiré, ou trop d'essais (message unique)
        """
        user = self.user_repository.get_active_by_email(self._normalize_email(email))
        if user is None:
            raise PasswordResetError(INVALID_CODE_MESSAGE)

        now = timezone.now()
        with transaction.atomic():
            challenge = self.challenge_repository.get_latest_open_for_user(user, lock=True)
            if challenge is None or now > challenge.expires_at or challenge.attempts >= MAX_ATTEMPTS:
                pass
            elif not hmac.compare_digest(self._digest(f"code:{user.pk}", code), challenge.code_hash):
                self.challenge_repository.increment_attempts(challenge)
            else:
                reset_token = secrets.token_urlsafe(32)
                self.challenge_repository.mark_code_verified(
                    challenge,
                    token_hash=self._digest('token', reset_token),
                    now=now,
                    token_expires_at=now + timedelta(minutes=RESET_TOKEN_TTL_MINUTES),
                )
                return reset_token

        # Échec : levé hors de la transaction pour que l'incrément des tentatives soit conservé
        raise PasswordResetError(INVALID_CODE_MESSAGE)

    # ------------------------------------------------------------------ étape 3
    def confirm_password_reset(self, reset_token: str, new_password: str):
        """
        Définit le nouveau mot de passe avec le reset_token, puis invalide les sessions existantes.

        Returns:
            L'utilisateur dont le mot de passe a été réinitialisé (pour le journal d'audit)

        Raises:
            PasswordResetError: token invalide/expiré/déjà utilisé, ou mot de passe refusé
        """
        now = timezone.now()
        with transaction.atomic():
            challenge = self.challenge_repository.get_by_token_hash(
                self._digest('token', reset_token), lock=True
            )
            if (
                challenge is None
                or challenge.token_used_at is not None
                or challenge.token_expires_at is None
                or now > challenge.token_expires_at
                or not challenge.user.is_active
            ):
                raise PasswordResetError(INVALID_TOKEN_MESSAGE)

            user = challenge.user
            try:
                validate_password(new_password, user)
            except ValidationError as error:
                # Le token n'est pas consommé : l'utilisateur peut corriger son mot de passe
                raise PasswordResetError(' '.join(error.messages))

            self.user_repository.update_password(user, new_password)
            self.challenge_repository.mark_token_used(challenge, now)
            self.challenge_repository.invalidate_open_for_user(user, now)
            self.user_repository.blacklist_refresh_tokens(user)
        return user
