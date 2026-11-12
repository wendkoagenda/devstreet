"""
Publication repository interface définissant le contrat pour l'accès aux données publications.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.communaute.models import Publication


class PublicationRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository publications.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les publication, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les publication filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, publication_id: int) -> Optional[Publication]:
        """
        Obtenir un publication par ID.

        Args:
            publication_id (int): L'ID du publication

        Returns:
            Optional[Publication]: Le publication si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Publication:
        """
        Créer un nouveau publication.

        Args:
            **kwargs: Données du publication

        Returns:
            Publication: Le publication créé
        """
        pass

    @abstractmethod
    def update(self, publication: Publication, **kwargs) -> Publication:
        """
        Mettre à jour un publication existant.

        Args:
            publication (Publication): Le publication à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Publication: Le publication mis à jour
        """
        pass

    @abstractmethod
    def delete(self, publication: Publication) -> bool:
        """
        Supprimer un publication.

        Args:
            publication (Publication): Le publication à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, publication_id: int) -> bool:
        """
        Vérifier si un publication existe par ID.

        Args:
            publication_id (int): L'ID du publication

        Returns:
            bool: True si le publication existe, False sinon
        """
        pass