"""
LikePublication service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.communaute.models import LikePublication
from app.communaute.repositories.likepublication_repository import LikePublicationRepository


class LikePublicationService:
    """
    Classe de service pour la logique métier liée aux like_publications.
    """

    def __init__(self):
        self.likepublication_repository = LikePublicationRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les like_publications, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les like_publications filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.likepublication_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, like_publication_id: int) -> Optional[LikePublication]:
        """
        Obtenir un like_publication par ID.
        
        Args:
            like_publication_id (int): L'ID du like_publication
            
        Returns:
            Optional[LikePublication]: Le like_publication si trouvé, None sinon
        """
        return self.likepublication_repository.get_by_id(like_publication_id)

    def create(self, like_publication_data: Dict[str, Any]) -> LikePublication:
        """
        Créer un nouveau like_publication avec validation.
        
        Args:
            like_publication_data (Dict[str, Any]): Données du like_publication
            
        Returns:
            LikePublication: Le like_publication créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(like_publication_data)
        
        return self.likepublication_repository.create(**like_publication_data)

    def update(self, like_publication_id: int, like_publication_data: Dict[str, Any], partial: bool = False) -> Optional[LikePublication]:
        """
        Mettre à jour un like_publication existant.
        
        Args:
            like_publication_id (int): L'ID du like_publication
            like_publication_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[LikePublication]: Le like_publication mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        like_publication = self.likepublication_repository.get_by_id(like_publication_id)
        if not like_publication:
            return None

        # Validation des données
        if not partial:
            self.validate_data(like_publication_data)

        return self.likepublication_repository.update(like_publication, **like_publication_data)

    def delete(self, like_publication_id: int) -> bool:
        """
        Supprimer un like_publication.
        
        Args:
            like_publication_id (int): L'ID du like_publication
            
        Returns:
            bool: True si supprimé avec succès, False si like_publication non trouvé
        """
        like_publication = self.likepublication_repository.get_by_id(like_publication_id)
        if not like_publication:
            return False

        return self.likepublication_repository.delete(like_publication)

    def validate_data(self, like_publication_data: Dict[str, Any]):
        """
        Valider les données du like_publication.
        
        Args:
            like_publication_data (Dict[str, Any]): Données du like_publication à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        # Ajoutez d'autres validations selon vos besoins