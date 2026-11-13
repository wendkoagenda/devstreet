"""
LienInvitation repository interface définissant le contrat pour l'accès aux données lieninvitations.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.communaute.models import LienInvitation


class LienInvitationRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository lieninvitations.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les lien_invitation, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les lien_invitation filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, lien_invitation_id: int) -> Optional[LienInvitation]:
        """
        Obtenir un lien_invitation par ID.

        Args:
            lien_invitation_id (int): L'ID du lien_invitation

        Returns:
            Optional[LienInvitation]: Le lien_invitation si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> LienInvitation:
        """
        Créer un nouveau lien_invitation.

        Args:
            **kwargs: Données du lien_invitation

        Returns:
            LienInvitation: Le lien_invitation créé
        """
        pass

    @abstractmethod
    def update(self, lien_invitation: LienInvitation, **kwargs) -> LienInvitation:
        """
        Mettre à jour un lien_invitation existant.

        Args:
            lien_invitation (LienInvitation): Le lien_invitation à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            LienInvitation: Le lien_invitation mis à jour
        """
        pass

    @abstractmethod
    def delete(self, lien_invitation: LienInvitation) -> bool:
        """
        Supprimer un lien_invitation.

        Args:
            lien_invitation (LienInvitation): Le lien_invitation à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, lien_invitation_id: int) -> bool:
        """
        Vérifier si un lien_invitation existe par ID.

        Args:
            lien_invitation_id (int): L'ID du lien_invitation

        Returns:
            bool: True si le lien_invitation existe, False sinon
        """
        pass