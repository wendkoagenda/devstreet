"""
Code de confirmation du changement de mot de passe (membre connecté).

1. request_code : envoie un code à 6 chiffres par e-mail (immédiatement : sans code, le membre ne peut pas continuer,
   un échec d'envoi lui est donc signalé).
2. consume_code : vérifie et consomme le code, juste avant que la vue applique le nouveau mot de passe.

Le mécanisme est celui du « mot de passe oublié » (code haché, durée de vie, tentatives limitées), avec le motif
`change` : un code de réinitialisation ne sert pas ici, et inversement.
"""
import hmac
import logging
import secrets
from datetime import timedelta
from typing import Optional

from django.db import transaction
from django.utils import timezone

from app.core.interfaces.password_reset_challenge_repository_interface import (
    PasswordResetChallengeRepositoryInterface,
)
from app.core.models import PasswordResetChallenge
from app.core.repositories.password_reset_challenge_repository import PasswordResetChallengeRepository
from app.core.services import email_catalog
from app.core.services.email_service import EmailService
from app.core.services.forgot_password_service import (
    CODE_LENGTH,
    CODE_TTL_MINUTES,
    MAX_ATTEMPTS,
    RESEND_COOLDOWN_SECONDS,
    ForgotPasswordService,
)

logger = logging.getLogger(__name__)

PURPOSE = PasswordResetChallenge.PURPOSE_CHANGE

CODE_SENT_MESSAGE = "Un code de confirmation vient d'être envoyé à votre adresse e-mail."
INVALID_CODE_MESSAGE = "Code invalide ou expiré. Redemandez un code si nécessaire."
NO_PASSWORD_MESSAGE = (
    "Votre compte n'a pas encore de mot de passe (connexion Google ou GitHub). "
    "Définissez-en un depuis la page « Mot de passe oublié »."
)
EMAIL_FAILED_MESSAGE = "Le code n'a pas pu être envoyé. Réessayez dans quelques instants."


class PasswordChangeError(Exception):
    """Erreur métier du changement de mot de passe (message destiné au membre)."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class PasswordChangeCodeService:
    """Envoi et vérification du code de changement de mot de passe."""

    def __init__(
        self,
        challenge_repository: Optional[PasswordResetChallengeRepositoryInterface] = None,
        email_service: Optional[EmailService] = None,
    ):
        self.challenge_repository = challenge_repository or PasswordResetChallengeRepository()
        self.email_service = email_service or EmailService()

    @staticmethod
    def _digest(user_id: int, code: str) -> str:
        # Préfixe distinct de celui du « mot de passe oublié » : les empreintes ne sont pas interchangeables
        return ForgotPasswordService._digest(f"change:{user_id}", code)

    def request_code(self, user) -> None:
        """
        Envoie un nouveau code (les précédents deviennent inutilisables).

        Raises:
            PasswordChangeError: compte sans mot de passe, demande trop rapprochée (429) ou échec d'envoi (503)
        """
        if not user.has_usable_password():
            raise PasswordChangeError(NO_PASSWORD_MESSAGE)

        now = timezone.now()
        last_created_at = self.challenge_repository.get_latest_created_at(user, purpose=PURPOSE)
        if last_created_at and (now - last_created_at).total_seconds() < RESEND_COOLDOWN_SECONDS:
            wait = RESEND_COOLDOWN_SECONDS - int((now - last_created_at).total_seconds())
            raise PasswordChangeError(f"Patientez {wait} secondes avant de redemander un code.", status_code=429)

        code = ''.join(secrets.choice('0123456789') for _ in range(CODE_LENGTH))
        try:
            with transaction.atomic():
                self.challenge_repository.invalidate_open_for_user(user, now, purpose=PURPOSE)
                self.challenge_repository.create(
                    user=user,
                    code_hash=self._digest(user.pk, code),
                    expires_at=now + timedelta(minutes=CODE_TTL_MINUTES),
                    purpose=PURPOSE,
                )
                self.email_service.send(
                    email_catalog.password_change_code(
                        user.email, user.first_name or user.username, code, CODE_TTL_MINUTES
                    )
                )
        except Exception as error:
            # Transaction annulée : le code n'existe pas, les précédents restent valides
            logger.error("Échec de l'envoi du code de changement de mot de passe (user_id=%s)", user.pk, exc_info=True)
            raise PasswordChangeError(EMAIL_FAILED_MESSAGE, status_code=503) from error

    def consume_code(self, user, code: str) -> None:
        """
        Vérifie le code et le consomme (usage unique).

        Raises:
            PasswordChangeError: code faux, expiré, déjà utilisé ou trop d'essais (message unique)
        """
        now = timezone.now()
        with transaction.atomic():
            challenge = self.challenge_repository.get_latest_open_for_user(user, lock=True, purpose=PURPOSE)
            if challenge is None or now > challenge.expires_at or challenge.attempts >= MAX_ATTEMPTS:
                pass
            elif not hmac.compare_digest(self._digest(user.pk, code), challenge.code_hash):
                self.challenge_repository.increment_attempts(challenge)
            else:
                self.challenge_repository.mark_code_used(challenge, now)
                return

        # Levé hors de la transaction pour que l'incrément des tentatives soit conservé
        raise PasswordChangeError(INVALID_CODE_MESSAGE)
