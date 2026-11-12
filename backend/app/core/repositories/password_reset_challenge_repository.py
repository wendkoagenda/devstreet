"""
Password reset challenge repository implementation for data access operations.
"""
from datetime import datetime
from typing import Optional
from django.contrib.auth import get_user_model
from django.db.models import F
from app.core.interfaces.password_reset_challenge_repository_interface import (
    PasswordResetChallengeRepositoryInterface,
)
from app.core.models import PasswordResetChallenge

User = get_user_model()


class PasswordResetChallengeRepository(PasswordResetChallengeRepositoryInterface):
    """
    Concrete implementation of password reset challenge repository operations.
    """

    def create(self, user: User, code_hash: str, expires_at: datetime) -> PasswordResetChallenge:
        """
        Create a new challenge.
        """
        return PasswordResetChallenge.objects.create(
            user=user,
            code_hash=code_hash,
            expires_at=expires_at,
        )

    def delete(self, challenge: PasswordResetChallenge) -> None:
        """
        Delete a challenge.
        """
        challenge.delete()

    def get_latest_created_at(self, user: User) -> Optional[datetime]:
        """
        Get the creation date of the most recent challenge of a user.
        """
        return (
            PasswordResetChallenge.objects
            .filter(user=user)
            .order_by('-created_at')
            .values_list('created_at', flat=True)
            .first()
        )

    def get_latest_open_for_user(self, user: User, lock: bool = False) -> Optional[PasswordResetChallenge]:
        """
        Get the most recent challenge whose code and token have not been consumed yet.
        """
        queryset = PasswordResetChallenge.objects.filter(
            user=user,
            code_used_at__isnull=True,
            token_used_at__isnull=True,
        ).order_by('-created_at')
        if lock:
            queryset = queryset.select_for_update()
        return queryset.first()

    def get_by_token_hash(self, token_hash: str, lock: bool = False) -> Optional[PasswordResetChallenge]:
        """
        Get a challenge by the digest of its reset token.
        """
        queryset = PasswordResetChallenge.objects.select_related('user').filter(reset_token_hash=token_hash)
        if lock:
            queryset = queryset.select_for_update(of=('self',))
        return queryset.first()

    def increment_attempts(self, challenge: PasswordResetChallenge) -> int:
        """
        Atomically increment the number of failed code attempts.
        """
        PasswordResetChallenge.objects.filter(pk=challenge.pk).update(attempts=F('attempts') + 1)
        challenge.refresh_from_db(fields=['attempts'])
        return challenge.attempts

    def mark_code_verified(
        self,
        challenge: PasswordResetChallenge,
        token_hash: str,
        now: datetime,
        token_expires_at: datetime,
    ) -> None:
        """
        Consume the code and attach the digest of the one-shot reset token.
        """
        challenge.code_used_at = now
        challenge.reset_token_hash = token_hash
        challenge.token_expires_at = token_expires_at
        challenge.save(update_fields=['code_used_at', 'reset_token_hash', 'token_expires_at'])

    def mark_token_used(self, challenge: PasswordResetChallenge, now: datetime) -> None:
        """
        Consume the reset token.
        """
        challenge.token_used_at = now
        challenge.save(update_fields=['token_used_at'])

    def invalidate_open_for_user(self, user: User, now: datetime) -> int:
        """
        Invalidate every challenge of the user whose token has not been consumed.
        """
        open_challenges = PasswordResetChallenge.objects.filter(user=user, token_used_at__isnull=True)
        open_challenges.filter(reset_token_hash__isnull=False).update(token_expires_at=now)
        return open_challenges.update(expires_at=now)

    def delete_expired(self, before: datetime) -> int:
        """
        Delete challenges created before the given date.
        """
        deleted, _ = PasswordResetChallenge.objects.filter(created_at__lt=before).delete()
        return deleted
