"""
LienInvitation service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.communaute.models import LienInvitation
from app.communaute.repositories.lieninvitation_repository import LienInvitationRepository


class LienInvitationService:
    """
    Classe de service pour la logique métier liée aux lien_invitations.
    """

    def __init__(self):
        self.lieninvitation_repository = LienInvitationRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les lien_invitations, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les lien_invitations filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.lieninvitation_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, lien_invitation_id: int) -> Optional[LienInvitation]:
        """
        Obtenir un lien_invitation par ID.
        
        Args:
            lien_invitation_id (int): L'ID du lien_invitation
            
        Returns:
            Optional[LienInvitation]: Le lien_invitation si trouvé, None sinon
        """
        return self.lieninvitation_repository.get_by_id(lien_invitation_id)

    def create(self, lien_invitation_data: Dict[str, Any]) -> LienInvitation:
        """
        Créer un nouveau lien_invitation avec validation.
        
        Args:
            lien_invitation_data (Dict[str, Any]): Données du lien_invitation
            
        Returns:
            LienInvitation: Le lien_invitation créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(lien_invitation_data)
        
        return self.lieninvitation_repository.create(**lien_invitation_data)

    def update(self, lien_invitation_id: int, lien_invitation_data: Dict[str, Any], partial: bool = False) -> Optional[LienInvitation]:
        """
        Mettre à jour un lien_invitation existant.
        
        Args:
            lien_invitation_id (int): L'ID du lien_invitation
            lien_invitation_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[LienInvitation]: Le lien_invitation mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        lien_invitation = self.lieninvitation_repository.get_by_id(lien_invitation_id)
        if not lien_invitation:
            return None

        # Validation des données
        if not partial:
            self.validate_data(lien_invitation_data)

        return self.lieninvitation_repository.update(lien_invitation, **lien_invitation_data)

    def delete(self, lien_invitation_id: int) -> bool:
        """
        Supprimer un lien_invitation.
        
        Args:
            lien_invitation_id (int): L'ID du lien_invitation
            
        Returns:
            bool: True si supprimé avec succès, False si lien_invitation non trouvé
        """
        lien_invitation = self.lieninvitation_repository.get_by_id(lien_invitation_id)
        if not lien_invitation:
            return False

        return self.lieninvitation_repository.delete(lien_invitation)

    def validate_data(self, lien_invitation_data: Dict[str, Any]):
        """
        Valider les données du lien_invitation.
        
        Args:
            lien_invitation_data (Dict[str, Any]): Données du lien_invitation à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        # Ajoutez d'autres validations selon vos besoins