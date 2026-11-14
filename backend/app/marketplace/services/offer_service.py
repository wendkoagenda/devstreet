"""
Offer service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.marketplace.models import Offer
from app.marketplace.repositories.offer_repository import OfferRepository


class OfferService:
    """
    Classe de service pour la logique métier liée aux offers.
    """

    def __init__(self):
        self.offer_repository = OfferRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les offers, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les offers filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.offer_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, offer_id: int) -> Optional[Offer]:
        """
        Obtenir un offer par ID.
        
        Args:
            offer_id (int): L'ID du offer
            
        Returns:
            Optional[Offer]: Le offer si trouvé, None sinon
        """
        return self.offer_repository.get_by_id(offer_id)

    def create(self, offer_data: Dict[str, Any]) -> Offer:
        """
        Créer un nouveau offer avec validation.
        
        Args:
            offer_data (Dict[str, Any]): Données du offer
            
        Returns:
            Offer: Le offer créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(offer_data)
        
        return self.offer_repository.create(**offer_data)

    def update(self, offer_id: int, offer_data: Dict[str, Any], partial: bool = False) -> Optional[Offer]:
        """
        Mettre à jour un offer existant.
        
        Args:
            offer_id (int): L'ID du offer
            offer_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[Offer]: Le offer mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        offer = self.offer_repository.get_by_id(offer_id)
        if not offer:
            return None

        # Validation des données
        if not partial:
            self.validate_data(offer_data)

        return self.offer_repository.update(offer, **offer_data)

    def delete(self, offer_id: int) -> bool:
        """
        Supprimer un offer.
        
        Args:
            offer_id (int): L'ID du offer
            
        Returns:
            bool: True si supprimé avec succès, False si offer non trouvé
        """
        offer = self.offer_repository.get_by_id(offer_id)
        if not offer:
            return False

        return self.offer_repository.delete(offer)

    def validate_data(self, offer_data: Dict[str, Any]):
        """
        Valider les données du offer.
        
        Args:
            offer_data (Dict[str, Any]): Données du offer à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        if 'type' in offer_data:
            _valid_type = ['mission', 'cdd', 'cdi', 'stage']
            if offer_data['type'] not in _valid_type:
                raise ValidationError("Valeur invalide pour le champ type")
        if 'experience_level' in offer_data:
            _valid_experience_level = ['junior', 'mid', 'senior', 'expert']
            if offer_data['experience_level'] not in _valid_experience_level:
                raise ValidationError("Valeur invalide pour le champ experience_level")
        if 'budget_period' in offer_data:
            _valid_budget_period = ['day', 'month', 'fixed']
            if offer_data['budget_period'] not in _valid_budget_period:
                raise ValidationError("Valeur invalide pour le champ budget_period")
        if 'work_mode' in offer_data:
            _valid_work_mode = ['on_site', 'hybrid', 'remote']
            if offer_data['work_mode'] not in _valid_work_mode:
                raise ValidationError("Valeur invalide pour le champ work_mode")
        if 'status' in offer_data:
            _valid_status = ['draft', 'open', 'closed']
            if offer_data['status'] not in _valid_status:
                raise ValidationError("Valeur invalide pour le champ status")
        # Ajoutez d'autres validations selon vos besoins