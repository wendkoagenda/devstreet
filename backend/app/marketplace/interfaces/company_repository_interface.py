"""
Company repository interface définissant le contrat pour l'accès aux données companys.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.marketplace.models import Company


class CompanyRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository companys.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les company, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les company filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, company_id: int) -> Optional[Company]:
        """
        Obtenir un company par ID.

        Args:
            company_id (int): L'ID du company

        Returns:
            Optional[Company]: Le company si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Company:
        """
        Créer un nouveau company.

        Args:
            **kwargs: Données du company

        Returns:
            Company: Le company créé
        """
        pass

    @abstractmethod
    def update(self, company: Company, **kwargs) -> Company:
        """
        Mettre à jour un company existant.

        Args:
            company (Company): Le company à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Company: Le company mis à jour
        """
        pass

    @abstractmethod
    def delete(self, company: Company) -> bool:
        """
        Supprimer un company.

        Args:
            company (Company): Le company à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, company_id: int) -> bool:
        """
        Vérifier si un company existe par ID.

        Args:
            company_id (int): L'ID du company

        Returns:
            bool: True si le company existe, False sinon
        """
        pass