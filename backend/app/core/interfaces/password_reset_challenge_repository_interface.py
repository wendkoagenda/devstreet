"""
Password reset challenge repository interface defining the contract for challenge data access.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from django.contrib.auth import get_user_model
from app.core.models import PasswordResetChallenge

User = get_user_model()


class PasswordResetChallengeRepositoryInterface(ABC):
    """
    Abstract interface for password reset challenge repository operations.
    """

    @abstractmethod
    def create(self, user: User, code_hash: str, expires_at: datetime) -> PasswordResetChallenge:
        """
        Create a new challenge.

        Args:
            user (User): The user requesting the reset
            code_hash (str): HMAC digest of the e-mailed code
            expires_at (datetime): Expiration of the code

        Returns:
            PasswordResetChallenge: The created challenge
        """
        pass

    @abstractmethod
    def delete(self, challenge: PasswordResetChallenge) -> None:
        """
        Delete a challenge.

        Args:
            challenge (PasswordResetChallenge): The challenge to delete
        """
        pass

    @abstractmethod
    def get_latest_created_at(self, user: User) -> Optional[datetime]:
        """
        Get the creation date of the most recent challenge of a user.

        Args:
            user (User): The user

        Returns:
            Optional[datetime]: Creation date, None if the user never requested a reset
        """
        pass

    @abstractmethod
    def get_latest_open_for_user(self, user: User, lock: bool = False) -> Optional[PasswordResetChallenge]:
        """
        Get the most recent challenge whose code has not been consumed yet.

        Args:
            user (User): The user
            lock (bool): Lock the row until the end of the transaction (SELECT ... FOR UPDATE)

        Returns:
            Optional[PasswordResetChallenge]: The challenge if any
        """
        pass

    @abstractmethod
    def get_by_token_hash(self, token_hash: str, lock: bool = False) -> Optional[PasswordResetChallenge]:
        """
        Get a challenge by the digest of its reset token.

        Args:
            token_hash (str): HMAC digest of the reset token
            lock (bool): Lock the row until the end of the transaction

        Returns:
            Optional[PasswordResetChallenge]: The challenge if any
        """
        pass

    @abstractmethod
    def increment_attempts(self, challenge: PasswordResetChallenge) -> int:
        """
        Atomically increment the number of failed code attempts.

        Args:
            challenge (PasswordResetChallenge): The challenge

        Returns:
            int: The new number of attempts
        """
        pass

    @abstractmethod
    def mark_code_verified(
        self,
        challenge: PasswordResetChallenge,
        token_hash: str,
        now: datetime,
        token_expires_at: datetime,
    ) -> None:
        """
        Consume the code and attach the digest of the one-shot reset token.

        Args:
            challenge (PasswordResetChallenge): The challenge
            token_hash (str): HMAC digest of the reset token
            now (datetime): Consumption date
            token_expires_at (datetime): Expiration of the token
        """
        pass

    @abstractmethod
    def mark_token_used(self, challenge: PasswordResetChallenge, now: datetime) -> None:
        """
        Consume the reset token.

        Args:
            challenge (PasswordResetChallenge): The challenge
            now (datetime): Consumption date
        """
        pass

    @abstractmethod
    def invalidate_open_for_user(self, user: User, now: datetime) -> int:
        """
        Invalidate every challenge of the user whose token has not been consumed
        (code and token expire immediately).

        Args:
            user (User): The user
            now (datetime): Invalidation date

        Returns:
            int: Number of invalidated challenges
        """
        pass

    @abstractmethod
    def delete_expired(self, before: datetime) -> int:
        """
        Delete challenges created before the given date.

        Args:
            before (datetime): Cut-off date

        Returns:
            int: Number of deleted challenges
        """
        pass
