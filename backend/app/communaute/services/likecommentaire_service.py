"""
LikeCommentaire service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.communaute.models import LikeCommentaire
from app.communaute.repositories.likecommentaire_repository import LikeCommentaireRepository


class LikeCommentaireService:
    """
    Classe de service pour la logique métier liée aux like_commentaires.
    """

    def __init__(self):
        self.likecommentaire_repository = LikeCommentaireRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les like_commentaires, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les like_commentaires filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.likecommentaire_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, like_commentaire_id: int) -> Optional[LikeCommentaire]:
        """
        Obtenir un like_commentaire par ID.
        
        Args:
            like_commentaire_id (int): L'ID du like_commentaire
            
        Returns:
            Optional[LikeCommentaire]: Le like_commentaire si trouvé, None sinon
        """
        return self.likecommentaire_repository.get_by_id(like_commentaire_id)

    def create(self, like_commentaire_data: Dict[str, Any]) -> LikeCommentaire:
        """
        Créer un nouveau like_commentaire avec validation.
        
        Args:
            like_commentaire_data (Dict[str, Any]): Données du like_commentaire
            
        Returns:
            LikeCommentaire: Le like_commentaire créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(like_commentaire_data)
        
        return self.likecommentaire_repository.create(**like_commentaire_data)

    def update(self, like_commentaire_id: int, like_commentaire_data: Dict[str, Any], partial: bool = False) -> Optional[LikeCommentaire]:
        """
        Mettre à jour un like_commentaire existant.
        
        Args:
            like_commentaire_id (int): L'ID du like_commentaire
            like_commentaire_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[LikeCommentaire]: Le like_commentaire mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        like_commentaire = self.likecommentaire_repository.get_by_id(like_commentaire_id)
        if not like_commentaire:
            return None

        # Validation des données
        if not partial:
            self.validate_data(like_commentaire_data)

        return self.likecommentaire_repository.update(like_commentaire, **like_commentaire_data)

    def delete(self, like_commentaire_id: int) -> bool:
        """
        Supprimer un like_commentaire.
        
        Args:
            like_commentaire_id (int): L'ID du like_commentaire
            
        Returns:
            bool: True si supprimé avec succès, False si like_commentaire non trouvé
        """
        like_commentaire = self.likecommentaire_repository.get_by_id(like_commentaire_id)
        if not like_commentaire:
            return False

        return self.likecommentaire_repository.delete(like_commentaire)

    def validate_data(self, like_commentaire_data: Dict[str, Any]):
        """
        Valider les données du like_commentaire.
        
        Args:
            like_commentaire_data (Dict[str, Any]): Données du like_commentaire à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        # Ajoutez d'autres validations selon vos besoins