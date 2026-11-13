"""
LikePublication repository interface définissant le contrat pour l'accès aux données likepublications.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.communaute.models import LikePublication


class LikePublicationRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository likepublications.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les like_publication, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les like_publication filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, like_publication_id: int) -> Optional[LikePublication]:
        """
        Obtenir un like_publication par ID.

        Args:
            like_publication_id (int): L'ID du like_publication

        Returns:
            Optional[LikePublication]: Le like_publication si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> LikePublication:
        """
        Créer un nouveau like_publication.

        Args:
            **kwargs: Données du like_publication

        Returns:
            LikePublication: Le like_publication créé
        """
        pass

    @abstractmethod
    def update(self, like_publication: LikePublication, **kwargs) -> LikePublication:
        """
        Mettre à jour un like_publication existant.

        Args:
            like_publication (LikePublication): Le like_publication à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            LikePublication: Le like_publication mis à jour
        """
        pass

    @abstractmethod
    def delete(self, like_publication: LikePublication) -> bool:
        """
        Supprimer un like_publication.

        Args:
            like_publication (LikePublication): Le like_publication à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, like_publication_id: int) -> bool:
        """
        Vérifier si un like_publication existe par ID.

        Args:
            like_publication_id (int): L'ID du like_publication

        Returns:
            bool: True si le like_publication existe, False sinon
        """
        pass