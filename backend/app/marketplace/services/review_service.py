"""
Review service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.marketplace.models import Review
from app.marketplace.repositories.review_repository import ReviewRepository


class ReviewService:
    """
    Classe de service pour la logique métier liée aux reviews.
    """

    def __init__(self):
        self.review_repository = ReviewRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les reviews, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les reviews filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.review_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, review_id: int) -> Optional[Review]:
        """
        Obtenir un review par ID.
        
        Args:
            review_id (int): L'ID du review
            
        Returns:
            Optional[Review]: Le review si trouvé, None sinon
        """
        return self.review_repository.get_by_id(review_id)

    def create(self, review_data: Dict[str, Any]) -> Review:
        """
        Créer un nouveau review avec validation.
        
        Args:
            review_data (Dict[str, Any]): Données du review
            
        Returns:
            Review: Le review créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(review_data)
        
        return self.review_repository.create(**review_data)

    def update(self, review_id: int, review_data: Dict[str, Any], partial: bool = False) -> Optional[Review]:
        """
        Mettre à jour un review existant.
        
        Args:
            review_id (int): L'ID du review
            review_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[Review]: Le review mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        review = self.review_repository.get_by_id(review_id)
        if not review:
            return None

        # Validation des données
        if not partial:
            self.validate_data(review_data)

        return self.review_repository.update(review, **review_data)

    def delete(self, review_id: int) -> bool:
        """
        Supprimer un review.
        
        Args:
            review_id (int): L'ID du review
            
        Returns:
            bool: True si supprimé avec succès, False si review non trouvé
        """
        review = self.review_repository.get_by_id(review_id)
        if not review:
            return False

        return self.review_repository.delete(review)

    def validate_data(self, review_data: Dict[str, Any]):
        """
        Valider les données du review.
        
        Args:
            review_data (Dict[str, Any]): Données du review à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        # Ajoutez d'autres validations selon vos besoins