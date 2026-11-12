"""
OptionPublication service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.communaute.models import OptionPublication
from app.communaute.repositories.optionpublication_repository import OptionPublicationRepository


class OptionPublicationService:
    """
    Classe de service pour la logique métier liée aux option_publications.
    """

    def __init__(self):
        self.optionpublication_repository = OptionPublicationRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les option_publications, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les option_publications filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.optionpublication_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, option_publication_id: int) -> Optional[OptionPublication]:
        """
        Obtenir un option_publication par ID.
        
        Args:
            option_publication_id (int): L'ID du option_publication
            
        Returns:
            Optional[OptionPublication]: Le option_publication si trouvé, None sinon
        """
        return self.optionpublication_repository.get_by_id(option_publication_id)

    def create(self, option_publication_data: Dict[str, Any]) -> OptionPublication:
        """
        Créer un nouveau option_publication avec validation.
        
        Args:
            option_publication_data (Dict[str, Any]): Données du option_publication
            
        Returns:
            OptionPublication: Le option_publication créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(option_publication_data)
        
        return self.optionpublication_repository.create(**option_publication_data)

    def update(self, option_publication_id: int, option_publication_data: Dict[str, Any], partial: bool = False) -> Optional[OptionPublication]:
        """
        Mettre à jour un option_publication existant.
        
        Args:
            option_publication_id (int): L'ID du option_publication
            option_publication_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[OptionPublication]: Le option_publication mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        option_publication = self.optionpublication_repository.get_by_id(option_publication_id)
        if not option_publication:
            return None

        # Validation des données
        if not partial:
            self.validate_data(option_publication_data)

        return self.optionpublication_repository.update(option_publication, **option_publication_data)

    def delete(self, option_publication_id: int) -> bool:
        """
        Supprimer un option_publication.
        
        Args:
            option_publication_id (int): L'ID du option_publication
            
        Returns:
            bool: True si supprimé avec succès, False si option_publication non trouvé
        """
        option_publication = self.optionpublication_repository.get_by_id(option_publication_id)
        if not option_publication:
            return False

        return self.optionpublication_repository.delete(option_publication)

    def validate_data(self, option_publication_data: Dict[str, Any]):
        """
        Valider les données du option_publication.
        
        Args:
            option_publication_data (Dict[str, Any]): Données du option_publication à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        # Ajoutez d'autres validations selon vos besoins