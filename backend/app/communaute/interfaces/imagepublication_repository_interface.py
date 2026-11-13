"""
ImagePublication repository interface définissant le contrat pour l'accès aux données imagepublications.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.communaute.models import ImagePublication


class ImagePublicationRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository imagepublications.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les image_publication, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les image_publication filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, image_publication_id: int) -> Optional[ImagePublication]:
        """
        Obtenir un image_publication par ID.

        Args:
            image_publication_id (int): L'ID du image_publication

        Returns:
            Optional[ImagePublication]: Le image_publication si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> ImagePublication:
        """
        Créer un nouveau image_publication.

        Args:
            **kwargs: Données du image_publication

        Returns:
            ImagePublication: Le image_publication créé
        """
        pass

    @abstractmethod
    def update(self, image_publication: ImagePublication, **kwargs) -> ImagePublication:
        """
        Mettre à jour un image_publication existant.

        Args:
            image_publication (ImagePublication): Le image_publication à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            ImagePublication: Le image_publication mis à jour
        """
        pass

    @abstractmethod
    def delete(self, image_publication: ImagePublication) -> bool:
        """
        Supprimer un image_publication.

        Args:
            image_publication (ImagePublication): Le image_publication à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, image_publication_id: int) -> bool:
        """
        Vérifier si un image_publication existe par ID.

        Args:
            image_publication_id (int): L'ID du image_publication

        Returns:
            bool: True si le image_publication existe, False sinon
        """
        pass