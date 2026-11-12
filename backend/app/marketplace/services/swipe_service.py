"""
Swipe service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.marketplace.models import Swipe
from app.marketplace.repositories.swipe_repository import SwipeRepository


class SwipeService:
    """
    Classe de service pour la logique métier liée aux swipes.
    """

    def __init__(self):
        self.swipe_repository = SwipeRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les swipes, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les swipes filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.swipe_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, swipe_id: int) -> Optional[Swipe]:
        """
        Obtenir un swipe par ID.
        
        Args:
            swipe_id (int): L'ID du swipe
            
        Returns:
            Optional[Swipe]: Le swipe si trouvé, None sinon
        """
        return self.swipe_repository.get_by_id(swipe_id)

    def create(self, swipe_data: Dict[str, Any]) -> Swipe:
        """
        Créer un nouveau swipe avec validation.
        
        Args:
            swipe_data (Dict[str, Any]): Données du swipe
            
        Returns:
            Swipe: Le swipe créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(swipe_data)
        
        return self.swipe_repository.create(**swipe_data)

    def update(self, swipe_id: int, swipe_data: Dict[str, Any], partial: bool = False) -> Optional[Swipe]:
        """
        Mettre à jour un swipe existant.
        
        Args:
            swipe_id (int): L'ID du swipe
            swipe_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[Swipe]: Le swipe mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        swipe = self.swipe_repository.get_by_id(swipe_id)
        if not swipe:
            return None

        # Validation des données
        if not partial:
            self.validate_data(swipe_data)

        return self.swipe_repository.update(swipe, **swipe_data)

    def delete(self, swipe_id: int) -> bool:
        """
        Supprimer un swipe.
        
        Args:
            swipe_id (int): L'ID du swipe
            
        Returns:
            bool: True si supprimé avec succès, False si swipe non trouvé
        """
        swipe = self.swipe_repository.get_by_id(swipe_id)
        if not swipe:
            return False

        return self.swipe_repository.delete(swipe)

    def validate_data(self, swipe_data: Dict[str, Any]):
        """
        Valider les données du swipe.
        
        Args:
            swipe_data (Dict[str, Any]): Données du swipe à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        if 'direction' in swipe_data:
            _valid_direction = ['like', 'pass']
            if swipe_data['direction'] not in _valid_direction:
                raise ValidationError("Valeur invalide pour le champ direction")
        if 'context' in swipe_data:
            _valid_context = ['recruit', 'network']
            if swipe_data['context'] not in _valid_context:
                raise ValidationError("Valeur invalide pour le champ context")
        # Ajoutez d'autres validations selon vos besoins