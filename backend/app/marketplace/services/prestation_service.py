"""
Prestation service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.marketplace.models import Prestation
from app.marketplace.repositories.prestation_repository import PrestationRepository
from app.metier.utils.file_field_utils import delete_instance_files, delete_replaced_files


class PrestationService:
    """
    Classe de service pour la logique métier liée aux prestations.
    """
    FILE_FIELD_NAMES = ["cover_image"]

    def __init__(self):
        self.prestation_repository = PrestationRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les prestations, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les prestations filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.prestation_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, prestation_id: int) -> Optional[Prestation]:
        """
        Obtenir un prestation par ID.
        
        Args:
            prestation_id (int): L'ID du prestation
            
        Returns:
            Optional[Prestation]: Le prestation si trouvé, None sinon
        """
        return self.prestation_repository.get_by_id(prestation_id)

    def create(self, prestation_data: Dict[str, Any]) -> Prestation:
        """
        Créer un nouveau prestation avec validation.
        
        Args:
            prestation_data (Dict[str, Any]): Données du prestation
            
        Returns:
            Prestation: Le prestation créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(prestation_data)
        
        return self.prestation_repository.create(**prestation_data)

    def update(self, prestation_id: int, prestation_data: Dict[str, Any], partial: bool = False) -> Optional[Prestation]:
        """
        Mettre à jour un prestation existant.
        
        Args:
            prestation_id (int): L'ID du prestation
            prestation_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[Prestation]: Le prestation mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        prestation = self.prestation_repository.get_by_id(prestation_id)
        if not prestation:
            return None

        delete_replaced_files(prestation, prestation_data, self.FILE_FIELD_NAMES)
        # Validation des données
        if not partial:
            self.validate_data(prestation_data)

        return self.prestation_repository.update(prestation, **prestation_data)

    def delete(self, prestation_id: int) -> bool:
        """
        Supprimer un prestation.
        
        Args:
            prestation_id (int): L'ID du prestation
            
        Returns:
            bool: True si supprimé avec succès, False si prestation non trouvé
        """
        prestation = self.prestation_repository.get_by_id(prestation_id)
        if not prestation:
            return False

        delete_instance_files(prestation, self.FILE_FIELD_NAMES)
        return self.prestation_repository.delete(prestation)

    def validate_data(self, prestation_data: Dict[str, Any]):
        """
        Valider les données du prestation.
        
        Args:
            prestation_data (Dict[str, Any]): Données du prestation à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        if 'category' in prestation_data:
            _valid_category = ['web', 'mobile', 'design', 'devops', 'data', 'other']
            if prestation_data['category'] not in _valid_category:
                raise ValidationError("Valeur invalide pour le champ category")
        # Ajoutez d'autres validations selon vos besoins