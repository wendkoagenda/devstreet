"""
ImagePublication service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.communaute.models import ImagePublication
from app.communaute.repositories.imagepublication_repository import ImagePublicationRepository


class ImagePublicationService:
    """
    Classe de service pour la logique métier liée aux image_publications.
    """

    def __init__(self):
        self.imagepublication_repository = ImagePublicationRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les image_publications, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les image_publications filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.imagepublication_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, image_publication_id: int) -> Optional[ImagePublication]:
        """
        Obtenir un image_publication par ID.
        
        Args:
            image_publication_id (int): L'ID du image_publication
            
        Returns:
            Optional[ImagePublication]: Le image_publication si trouvé, None sinon
        """
        return self.imagepublication_repository.get_by_id(image_publication_id)

    def create(self, image_publication_data: Dict[str, Any]) -> ImagePublication:
        """
        Créer un nouveau image_publication avec validation.
        
        Args:
            image_publication_data (Dict[str, Any]): Données du image_publication
            
        Returns:
            ImagePublication: Le image_publication créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(image_publication_data)
        
        return self.imagepublication_repository.create(**image_publication_data)

    def update(self, image_publication_id: int, image_publication_data: Dict[str, Any], partial: bool = False) -> Optional[ImagePublication]:
        """
        Mettre à jour un image_publication existant.
        
        Args:
            image_publication_id (int): L'ID du image_publication
            image_publication_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[ImagePublication]: Le image_publication mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        image_publication = self.imagepublication_repository.get_by_id(image_publication_id)
        if not image_publication:
            return None

        # Validation des données
        if not partial:
            self.validate_data(image_publication_data)

        return self.imagepublication_repository.update(image_publication, **image_publication_data)

    def delete(self, image_publication_id: int) -> bool:
        """
        Supprimer un image_publication.
        
        Args:
            image_publication_id (int): L'ID du image_publication
            
        Returns:
            bool: True si supprimé avec succès, False si image_publication non trouvé
        """
        image_publication = self.imagepublication_repository.get_by_id(image_publication_id)
        if not image_publication:
            return False

        return self.imagepublication_repository.delete(image_publication)

    def validate_data(self, image_publication_data: Dict[str, Any]):
        """
        Valider les données du image_publication.
        
        Args:
            image_publication_data (Dict[str, Any]): Données du image_publication à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        # Ajoutez d'autres validations selon vos besoins