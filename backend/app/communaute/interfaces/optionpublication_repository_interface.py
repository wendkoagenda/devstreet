"""
OptionPublication repository interface définissant le contrat pour l'accès aux données optionpublications.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.communaute.models import OptionPublication


class OptionPublicationRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository optionpublications.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les option_publication, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les option_publication filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, option_publication_id: int) -> Optional[OptionPublication]:
        """
        Obtenir un option_publication par ID.

        Args:
            option_publication_id (int): L'ID du option_publication

        Returns:
            Optional[OptionPublication]: Le option_publication si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> OptionPublication:
        """
        Créer un nouveau option_publication.

        Args:
            **kwargs: Données du option_publication

        Returns:
            OptionPublication: Le option_publication créé
        """
        pass

    @abstractmethod
    def update(self, option_publication: OptionPublication, **kwargs) -> OptionPublication:
        """
        Mettre à jour un option_publication existant.

        Args:
            option_publication (OptionPublication): Le option_publication à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            OptionPublication: Le option_publication mis à jour
        """
        pass

    @abstractmethod
    def delete(self, option_publication: OptionPublication) -> bool:
        """
        Supprimer un option_publication.

        Args:
            option_publication (OptionPublication): Le option_publication à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, option_publication_id: int) -> bool:
        """
        Vérifier si un option_publication existe par ID.

        Args:
            option_publication_id (int): L'ID du option_publication

        Returns:
            bool: True si le option_publication existe, False sinon
        """
        pass