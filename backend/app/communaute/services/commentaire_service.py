"""
Commentaire service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.communaute.models import Commentaire
from app.communaute.repositories.commentaire_repository import CommentaireRepository


class CommentaireService:
    """
    Classe de service pour la logique métier liée aux commentaires.
    """

    def __init__(self):
        self.commentaire_repository = CommentaireRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les commentaires, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les commentaires filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.commentaire_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, commentaire_id: int) -> Optional[Commentaire]:
        """
        Obtenir un commentaire par ID.
        
        Args:
            commentaire_id (int): L'ID du commentaire
            
        Returns:
            Optional[Commentaire]: Le commentaire si trouvé, None sinon
        """
        return self.commentaire_repository.get_by_id(commentaire_id)

    def create(self, commentaire_data: Dict[str, Any]) -> Commentaire:
        """
        Créer un nouveau commentaire avec validation.
        
        Args:
            commentaire_data (Dict[str, Any]): Données du commentaire
            
        Returns:
            Commentaire: Le commentaire créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(commentaire_data)
        
        return self.commentaire_repository.create(**commentaire_data)

    def update(self, commentaire_id: int, commentaire_data: Dict[str, Any], partial: bool = False) -> Optional[Commentaire]:
        """
        Mettre à jour un commentaire existant.
        
        Args:
            commentaire_id (int): L'ID du commentaire
            commentaire_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[Commentaire]: Le commentaire mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        commentaire = self.commentaire_repository.get_by_id(commentaire_id)
        if not commentaire:
            return None

        # Validation des données
        if not partial:
            self.validate_data(commentaire_data)

        return self.commentaire_repository.update(commentaire, **commentaire_data)

    def delete(self, commentaire_id: int) -> bool:
        """
        Supprimer un commentaire.
        
        Args:
            commentaire_id (int): L'ID du commentaire
            
        Returns:
            bool: True si supprimé avec succès, False si commentaire non trouvé
        """
        commentaire = self.commentaire_repository.get_by_id(commentaire_id)
        if not commentaire:
            return False

        return self.commentaire_repository.delete(commentaire)

    def validate_data(self, commentaire_data: Dict[str, Any]):
        """
        Valider les données du commentaire.
        
        Args:
            commentaire_data (Dict[str, Any]): Données du commentaire à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        if 'nature' in commentaire_data:
            _valid_nature = ['COMMENTAIRE', 'RETOUR_APP', 'REPONSE_TECHNIQUE']
            if commentaire_data['nature'] not in _valid_nature:
                raise ValidationError("Valeur invalide pour le champ nature")
        # Ajoutez d'autres validations selon vos besoins