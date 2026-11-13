"""
ParticipationEspace service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.communaute.models import ParticipationEspace
from app.communaute.repositories.participationespace_repository import ParticipationEspaceRepository


class ParticipationEspaceService:
    """
    Classe de service pour la logique métier liée aux participation_espaces.
    """

    def __init__(self):
        self.participationespace_repository = ParticipationEspaceRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les participation_espaces, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les participation_espaces filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.participationespace_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, participation_espace_id: int) -> Optional[ParticipationEspace]:
        """
        Obtenir un participation_espace par ID.
        
        Args:
            participation_espace_id (int): L'ID du participation_espace
            
        Returns:
            Optional[ParticipationEspace]: Le participation_espace si trouvé, None sinon
        """
        return self.participationespace_repository.get_by_id(participation_espace_id)

    def create(self, participation_espace_data: Dict[str, Any]) -> ParticipationEspace:
        """
        Créer un nouveau participation_espace avec validation.
        
        Args:
            participation_espace_data (Dict[str, Any]): Données du participation_espace
            
        Returns:
            ParticipationEspace: Le participation_espace créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(participation_espace_data)
        
        return self.participationespace_repository.create(**participation_espace_data)

    def update(self, participation_espace_id: int, participation_espace_data: Dict[str, Any], partial: bool = False) -> Optional[ParticipationEspace]:
        """
        Mettre à jour un participation_espace existant.
        
        Args:
            participation_espace_id (int): L'ID du participation_espace
            participation_espace_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[ParticipationEspace]: Le participation_espace mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        participation_espace = self.participationespace_repository.get_by_id(participation_espace_id)
        if not participation_espace:
            return None

        # Validation des données
        if not partial:
            self.validate_data(participation_espace_data)

        return self.participationespace_repository.update(participation_espace, **participation_espace_data)

    def delete(self, participation_espace_id: int) -> bool:
        """
        Supprimer un participation_espace.
        
        Args:
            participation_espace_id (int): L'ID du participation_espace
            
        Returns:
            bool: True si supprimé avec succès, False si participation_espace non trouvé
        """
        participation_espace = self.participationespace_repository.get_by_id(participation_espace_id)
        if not participation_espace:
            return False

        return self.participationespace_repository.delete(participation_espace)

    def validate_data(self, participation_espace_data: Dict[str, Any]):
        """
        Valider les données du participation_espace.
        
        Args:
            participation_espace_data (Dict[str, Any]): Données du participation_espace à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        if 'role' in participation_espace_data:
            _valid_role = ['SUPER_ADMIN', 'ADMIN', 'MEMBRE']
            if participation_espace_data['role'] not in _valid_role:
                raise ValidationError("Valeur invalide pour le champ role")
        # Ajoutez d'autres validations selon vos besoins