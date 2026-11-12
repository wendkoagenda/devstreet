"""
Commentaire repository interface définissant le contrat pour l'accès aux données commentaires.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.communaute.models import Commentaire


class CommentaireRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository commentaires.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les commentaire, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les commentaire filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, commentaire_id: int) -> Optional[Commentaire]:
        """
        Obtenir un commentaire par ID.

        Args:
            commentaire_id (int): L'ID du commentaire

        Returns:
            Optional[Commentaire]: Le commentaire si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> Commentaire:
        """
        Créer un nouveau commentaire.

        Args:
            **kwargs: Données du commentaire

        Returns:
            Commentaire: Le commentaire créé
        """
        pass

    @abstractmethod
    def update(self, commentaire: Commentaire, **kwargs) -> Commentaire:
        """
        Mettre à jour un commentaire existant.

        Args:
            commentaire (Commentaire): Le commentaire à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Commentaire: Le commentaire mis à jour
        """
        pass

    @abstractmethod
    def delete(self, commentaire: Commentaire) -> bool:
        """
        Supprimer un commentaire.

        Args:
            commentaire (Commentaire): Le commentaire à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, commentaire_id: int) -> bool:
        """
        Vérifier si un commentaire existe par ID.

        Args:
            commentaire_id (int): L'ID du commentaire

        Returns:
            bool: True si le commentaire existe, False sinon
        """
        pass