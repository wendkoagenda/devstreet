"""
Availability service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.marketplace.models import Availability
from app.marketplace.repositories.availability_repository import AvailabilityRepository


class AvailabilityService:
    """
    Classe de service pour la logique métier liée aux availabilitys.
    """

    def __init__(self):
        self.availability_repository = AvailabilityRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les availabilitys, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les availabilitys filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.availability_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, availability_id: int) -> Optional[Availability]:
        """
        Obtenir un availability par ID.
        
        Args:
            availability_id (int): L'ID du availability
            
        Returns:
            Optional[Availability]: Le availability si trouvé, None sinon
        """
        return self.availability_repository.get_by_id(availability_id)

    def create(self, availability_data: Dict[str, Any]) -> Availability:
        """
        Créer un nouveau availability avec validation.
        
        Args:
            availability_data (Dict[str, Any]): Données du availability
            
        Returns:
            Availability: Le availability créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(availability_data)
        
        return self.availability_repository.create(**availability_data)

    def update(self, availability_id: int, availability_data: Dict[str, Any], partial: bool = False) -> Optional[Availability]:
        """
        Mettre à jour un availability existant.
        
        Args:
            availability_id (int): L'ID du availability
            availability_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[Availability]: Le availability mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        availability = self.availability_repository.get_by_id(availability_id)
        if not availability:
            return None

        # Validation des données
        if not partial:
            self.validate_data(availability_data)

        return self.availability_repository.update(availability, **availability_data)

    def delete(self, availability_id: int) -> bool:
        """
        Supprimer un availability.
        
        Args:
            availability_id (int): L'ID du availability
            
        Returns:
            bool: True si supprimé avec succès, False si availability non trouvé
        """
        availability = self.availability_repository.get_by_id(availability_id)
        if not availability:
            return False

        return self.availability_repository.delete(availability)

    def validate_data(self, availability_data: Dict[str, Any]):
        """
        Valider les données du availability.
        
        Args:
            availability_data (Dict[str, Any]): Données du availability à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        if 'status' in availability_data:
            _valid_status = ['available', 'partial', 'busy', 'leave']
            if availability_data['status'] not in _valid_status:
                raise ValidationError("Valeur invalide pour le champ status")
        if 'source' in availability_data:
            _valid_source = ['manual', 'mission']
            if availability_data['source'] not in _valid_source:
                raise ValidationError("Valeur invalide pour le champ source")
        # Ajoutez d'autres validations selon vos besoins