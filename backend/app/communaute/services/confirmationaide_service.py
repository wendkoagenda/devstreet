"""
ConfirmationAide service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.communaute.models import ConfirmationAide
from app.communaute.repositories.confirmationaide_repository import ConfirmationAideRepository


class ConfirmationAideService:
    """
    Classe de service pour la logique métier liée aux confirmation_aides.
    """

    def __init__(self):
        self.confirmationaide_repository = ConfirmationAideRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les confirmation_aides, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les confirmation_aides filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.confirmationaide_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, confirmation_aide_id: int) -> Optional[ConfirmationAide]:
        """
        Obtenir un confirmation_aide par ID.
        
        Args:
            confirmation_aide_id (int): L'ID du confirmation_aide
            
        Returns:
            Optional[ConfirmationAide]: Le confirmation_aide si trouvé, None sinon
        """
        return self.confirmationaide_repository.get_by_id(confirmation_aide_id)

    def create(self, confirmation_aide_data: Dict[str, Any]) -> ConfirmationAide:
        """
        Créer un nouveau confirmation_aide avec validation.
        
        Args:
            confirmation_aide_data (Dict[str, Any]): Données du confirmation_aide
            
        Returns:
            ConfirmationAide: Le confirmation_aide créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(confirmation_aide_data)
        
        return self.confirmationaide_repository.create(**confirmation_aide_data)

    def update(self, confirmation_aide_id: int, confirmation_aide_data: Dict[str, Any], partial: bool = False) -> Optional[ConfirmationAide]:
        """
        Mettre à jour un confirmation_aide existant.
        
        Args:
            confirmation_aide_id (int): L'ID du confirmation_aide
            confirmation_aide_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[ConfirmationAide]: Le confirmation_aide mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        confirmation_aide = self.confirmationaide_repository.get_by_id(confirmation_aide_id)
        if not confirmation_aide:
            return None

        # Validation des données
        if not partial:
            self.validate_data(confirmation_aide_data)

        return self.confirmationaide_repository.update(confirmation_aide, **confirmation_aide_data)

    def delete(self, confirmation_aide_id: int) -> bool:
        """
        Supprimer un confirmation_aide.
        
        Args:
            confirmation_aide_id (int): L'ID du confirmation_aide
            
        Returns:
            bool: True si supprimé avec succès, False si confirmation_aide non trouvé
        """
        confirmation_aide = self.confirmationaide_repository.get_by_id(confirmation_aide_id)
        if not confirmation_aide:
            return False

        return self.confirmationaide_repository.delete(confirmation_aide)

    def validate_data(self, confirmation_aide_data: Dict[str, Any]):
        """
        Valider les données du confirmation_aide.
        
        Args:
            confirmation_aide_data (Dict[str, Any]): Données du confirmation_aide à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        # Ajoutez d'autres validations selon vos besoins