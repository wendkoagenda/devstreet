"""
Espace service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.communaute.models import Espace
from app.communaute.repositories.espace_repository import EspaceRepository


class EspaceService:
    """
    Classe de service pour la logique métier liée aux espaces.
    """

    def __init__(self):
        self.espace_repository = EspaceRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les espaces, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les espaces filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.espace_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, espace_id: int) -> Optional[Espace]:
        """
        Obtenir un espace par ID.
        
        Args:
            espace_id (int): L'ID du espace
            
        Returns:
            Optional[Espace]: Le espace si trouvé, None sinon
        """
        return self.espace_repository.get_by_id(espace_id)

    def create(self, espace_data: Dict[str, Any]) -> Espace:
        """
        Créer un nouveau espace avec validation.
        
        Args:
            espace_data (Dict[str, Any]): Données du espace
            
        Returns:
            Espace: Le espace créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(espace_data)
        
        return self.espace_repository.create(**espace_data)

    def update(self, espace_id: int, espace_data: Dict[str, Any], partial: bool = False) -> Optional[Espace]:
        """
        Mettre à jour un espace existant.
        
        Args:
            espace_id (int): L'ID du espace
            espace_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[Espace]: Le espace mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        espace = self.espace_repository.get_by_id(espace_id)
        if not espace:
            return None

        # Validation des données
        if not partial:
            self.validate_data(espace_data)

        return self.espace_repository.update(espace, **espace_data)

    def delete(self, espace_id: int) -> bool:
        """
        Supprimer un espace.
        
        Args:
            espace_id (int): L'ID du espace
            
        Returns:
            bool: True si supprimé avec succès, False si espace non trouvé
        """
        espace = self.espace_repository.get_by_id(espace_id)
        if not espace:
            return False

        return self.espace_repository.delete(espace)

    def validate_data(self, espace_data: Dict[str, Any]):
        """
        Valider les données du espace.
        
        Args:
            espace_data (Dict[str, Any]): Données du espace à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        if 'type' in espace_data:
            _valid_type = ['COMMUNAUTE', 'CHAINE']
            if espace_data['type'] not in _valid_type:
                raise ValidationError("Valeur invalide pour le champ type")
        if 'acces' in espace_data:
            _valid_acces = ['PUBLIC', 'LIEN']
            if espace_data['acces'] not in _valid_acces:
                raise ValidationError("Valeur invalide pour le champ acces")
        # Ajoutez d'autres validations selon vos besoins