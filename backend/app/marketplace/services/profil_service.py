"""
Profil service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.marketplace.models import Profil
from app.marketplace.repositories.profil_repository import ProfilRepository
from app.metier.utils.file_field_utils import delete_instance_files, delete_replaced_files


class ProfilService:
    """
    Classe de service pour la logique métier liée aux profils.
    """
    FILE_FIELD_NAMES = ["photo"]

    def __init__(self):
        self.profil_repository = ProfilRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les profils, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les profils filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.profil_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, profil_id: int) -> Optional[Profil]:
        """
        Obtenir un profil par ID.
        
        Args:
            profil_id (int): L'ID du profil
            
        Returns:
            Optional[Profil]: Le profil si trouvé, None sinon
        """
        return self.profil_repository.get_by_id(profil_id)

    def create(self, profil_data: Dict[str, Any]) -> Profil:
        """
        Créer un nouveau profil avec validation.
        
        Args:
            profil_data (Dict[str, Any]): Données du profil
            
        Returns:
            Profil: Le profil créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(profil_data)
        
        return self.profil_repository.create(**profil_data)

    def update(self, profil_id: int, profil_data: Dict[str, Any], partial: bool = False) -> Optional[Profil]:
        """
        Mettre à jour un profil existant.
        
        Args:
            profil_id (int): L'ID du profil
            profil_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[Profil]: Le profil mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        profil = self.profil_repository.get_by_id(profil_id)
        if not profil:
            return None

        delete_replaced_files(profil, profil_data, self.FILE_FIELD_NAMES)
        # Validation des données
        if not partial:
            self.validate_data(profil_data)

        return self.profil_repository.update(profil, **profil_data)

    def delete(self, profil_id: int) -> bool:
        """
        Supprimer un profil.
        
        Args:
            profil_id (int): L'ID du profil
            
        Returns:
            bool: True si supprimé avec succès, False si profil non trouvé
        """
        profil = self.profil_repository.get_by_id(profil_id)
        if not profil:
            return False

        delete_instance_files(profil, self.FILE_FIELD_NAMES)
        return self.profil_repository.delete(profil)

    def validate_data(self, profil_data: Dict[str, Any]):
        """
        Valider les données du profil.
        
        Args:
            profil_data (Dict[str, Any]): Données du profil à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        if 'cv_visibility' in profil_data:
            _valid_cv_visibility = ['public', 'companies', 'private']
            if profil_data['cv_visibility'] not in _valid_cv_visibility:
                raise ValidationError("Valeur invalide pour le champ cv_visibility")
        # Ajoutez d'autres validations selon vos besoins