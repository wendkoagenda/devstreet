"""
VoteSondage service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.communaute.models import VoteSondage
from app.communaute.repositories.votesondage_repository import VoteSondageRepository


class VoteSondageService:
    """
    Classe de service pour la logique métier liée aux vote_sondages.
    """

    def __init__(self):
        self.votesondage_repository = VoteSondageRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les vote_sondages, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les vote_sondages filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.votesondage_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, vote_sondage_id: int) -> Optional[VoteSondage]:
        """
        Obtenir un vote_sondage par ID.
        
        Args:
            vote_sondage_id (int): L'ID du vote_sondage
            
        Returns:
            Optional[VoteSondage]: Le vote_sondage si trouvé, None sinon
        """
        return self.votesondage_repository.get_by_id(vote_sondage_id)

    def create(self, vote_sondage_data: Dict[str, Any]) -> VoteSondage:
        """
        Créer un nouveau vote_sondage avec validation.
        
        Args:
            vote_sondage_data (Dict[str, Any]): Données du vote_sondage
            
        Returns:
            VoteSondage: Le vote_sondage créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(vote_sondage_data)
        
        return self.votesondage_repository.create(**vote_sondage_data)

    def update(self, vote_sondage_id: int, vote_sondage_data: Dict[str, Any], partial: bool = False) -> Optional[VoteSondage]:
        """
        Mettre à jour un vote_sondage existant.
        
        Args:
            vote_sondage_id (int): L'ID du vote_sondage
            vote_sondage_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[VoteSondage]: Le vote_sondage mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        vote_sondage = self.votesondage_repository.get_by_id(vote_sondage_id)
        if not vote_sondage:
            return None

        # Validation des données
        if not partial:
            self.validate_data(vote_sondage_data)

        return self.votesondage_repository.update(vote_sondage, **vote_sondage_data)

    def delete(self, vote_sondage_id: int) -> bool:
        """
        Supprimer un vote_sondage.
        
        Args:
            vote_sondage_id (int): L'ID du vote_sondage
            
        Returns:
            bool: True si supprimé avec succès, False si vote_sondage non trouvé
        """
        vote_sondage = self.votesondage_repository.get_by_id(vote_sondage_id)
        if not vote_sondage:
            return False

        return self.votesondage_repository.delete(vote_sondage)

    def validate_data(self, vote_sondage_data: Dict[str, Any]):
        """
        Valider les données du vote_sondage.
        
        Args:
            vote_sondage_data (Dict[str, Any]): Données du vote_sondage à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        # Ajoutez d'autres validations selon vos besoins