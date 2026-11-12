"""
Fusion service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.metier.models import Fusion
from app.metier.repositories.fusion_repository import FusionRepository
from app.metier.utils.file_field_utils import delete_instance_files, delete_replaced_files


class FusionService:
    """
    Classe de service pour la logique métier liée aux fusions.
    """
    FILE_FIELD_NAMES = ["document"]

    def __init__(self):
        self.fusion_repository = FusionRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les fusions, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les fusions filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.fusion_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, fusion_id: int) -> Optional[Fusion]:
        """
        Obtenir un fusion par ID.
        
        Args:
            fusion_id (int): L'ID du fusion
            
        Returns:
            Optional[Fusion]: Le fusion si trouvé, None sinon
        """
        return self.fusion_repository.get_by_id(fusion_id)

    def create(self, fusion_data: Dict[str, Any]) -> Fusion:
        """
        Créer un nouveau fusion avec validation.
        
        Args:
            fusion_data (Dict[str, Any]): Données du fusion
            
        Returns:
            Fusion: Le fusion créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(fusion_data)
        
        return self.fusion_repository.create(**fusion_data)

    def update(self, fusion_id: int, fusion_data: Dict[str, Any], partial: bool = False) -> Optional[Fusion]:
        """
        Mettre à jour un fusion existant.
        
        Args:
            fusion_id (int): L'ID du fusion
            fusion_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[Fusion]: Le fusion mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        fusion = self.fusion_repository.get_by_id(fusion_id)
        if not fusion:
            return None

        delete_replaced_files(fusion, fusion_data, self.FILE_FIELD_NAMES)
        # Validation des données
        if not partial:
            self.validate_data(fusion_data)

        return self.fusion_repository.update(fusion, **fusion_data)

    def delete(self, fusion_id: int) -> bool:
        """
        Supprimer un fusion.
        
        Args:
            fusion_id (int): L'ID du fusion
            
        Returns:
            bool: True si supprimé avec succès, False si fusion non trouvé
        """
        fusion = self.fusion_repository.get_by_id(fusion_id)
        if not fusion:
            return False

        delete_instance_files(fusion, self.FILE_FIELD_NAMES)
        return self.fusion_repository.delete(fusion)

    def validate_data(self, fusion_data: Dict[str, Any]):
        """
        Valider les données du fusion.
        
        Args:
            fusion_data (Dict[str, Any]): Données du fusion à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        if 'titre' in fusion_data and not fusion_data['titre'].strip():
            raise ValidationError("Le champ titre ne peut pas être vide")
        if 'statut' in fusion_data and not fusion_data['statut'].strip():
            raise ValidationError("Le champ statut ne peut pas être vide")
        if 'statut' in fusion_data:
            _valid_statut = ['draft', 'published', 'archived']
            if fusion_data['statut'] not in _valid_statut:
                raise ValidationError("Valeur invalide pour le champ statut")
        # Ajoutez d'autres validations selon vos besoins