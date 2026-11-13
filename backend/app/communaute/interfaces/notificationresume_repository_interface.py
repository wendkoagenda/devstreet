"""
NotificationResume repository interface définissant le contrat pour l'accès aux données notificationresumes.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.communaute.models import NotificationResume


class NotificationResumeRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository notificationresumes.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les notification_resume, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les notification_resume filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, notification_resume_id: int) -> Optional[NotificationResume]:
        """
        Obtenir un notification_resume par ID.

        Args:
            notification_resume_id (int): L'ID du notification_resume

        Returns:
            Optional[NotificationResume]: Le notification_resume si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> NotificationResume:
        """
        Créer un nouveau notification_resume.

        Args:
            **kwargs: Données du notification_resume

        Returns:
            NotificationResume: Le notification_resume créé
        """
        pass

    @abstractmethod
    def update(self, notification_resume: NotificationResume, **kwargs) -> NotificationResume:
        """
        Mettre à jour un notification_resume existant.

        Args:
            notification_resume (NotificationResume): Le notification_resume à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            NotificationResume: Le notification_resume mis à jour
        """
        pass

    @abstractmethod
    def delete(self, notification_resume: NotificationResume) -> bool:
        """
        Supprimer un notification_resume.

        Args:
            notification_resume (NotificationResume): Le notification_resume à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, notification_resume_id: int) -> bool:
        """
        Vérifier si un notification_resume existe par ID.

        Args:
            notification_resume_id (int): L'ID du notification_resume

        Returns:
            bool: True si le notification_resume existe, False sinon
        """
        pass