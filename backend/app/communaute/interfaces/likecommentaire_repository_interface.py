"""
LikeCommentaire repository interface définissant le contrat pour l'accès aux données likecommentaires.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.communaute.models import LikeCommentaire


class LikeCommentaireRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository likecommentaires.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les like_commentaire, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les like_commentaire filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, like_commentaire_id: int) -> Optional[LikeCommentaire]:
        """
        Obtenir un like_commentaire par ID.

        Args:
            like_commentaire_id (int): L'ID du like_commentaire

        Returns:
            Optional[LikeCommentaire]: Le like_commentaire si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> LikeCommentaire:
        """
        Créer un nouveau like_commentaire.

        Args:
            **kwargs: Données du like_commentaire

        Returns:
            LikeCommentaire: Le like_commentaire créé
        """
        pass

    @abstractmethod
    def update(self, like_commentaire: LikeCommentaire, **kwargs) -> LikeCommentaire:
        """
        Mettre à jour un like_commentaire existant.

        Args:
            like_commentaire (LikeCommentaire): Le like_commentaire à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            LikeCommentaire: Le like_commentaire mis à jour
        """
        pass

    @abstractmethod
    def delete(self, like_commentaire: LikeCommentaire) -> bool:
        """
        Supprimer un like_commentaire.

        Args:
            like_commentaire (LikeCommentaire): Le like_commentaire à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, like_commentaire_id: int) -> bool:
        """
        Vérifier si un like_commentaire existe par ID.

        Args:
            like_commentaire_id (int): L'ID du like_commentaire

        Returns:
            bool: True si le like_commentaire existe, False sinon
        """
        pass