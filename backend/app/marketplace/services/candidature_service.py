"""
Candidature service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.marketplace.models import Candidature
from app.marketplace.repositories.candidature_repository import CandidatureRepository
from app.metier.utils.file_field_utils import delete_instance_files, delete_replaced_files


class CandidatureService:
    """
    Classe de service pour la logique métier liée aux candidatures.
    """
    FILE_FIELD_NAMES = ["cv_snapshot"]

    def __init__(self):
        self.candidature_repository = CandidatureRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les candidatures, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les candidatures filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.candidature_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, candidature_id: int) -> Optional[Candidature]:
        """
        Obtenir un candidature par ID.
        
        Args:
            candidature_id (int): L'ID du candidature
            
        Returns:
            Optional[Candidature]: Le candidature si trouvé, None sinon
        """
        return self.candidature_repository.get_by_id(candidature_id)

    def create(self, candidature_data: Dict[str, Any]) -> Candidature:
        """
        Créer un nouveau candidature avec validation.
        
        Args:
            candidature_data (Dict[str, Any]): Données du candidature
            
        Returns:
            Candidature: Le candidature créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(candidature_data)
        
        return self.candidature_repository.create(**candidature_data)

    def update(self, candidature_id: int, candidature_data: Dict[str, Any], partial: bool = False) -> Optional[Candidature]:
        """
        Mettre à jour un candidature existant.
        
        Args:
            candidature_id (int): L'ID du candidature
            candidature_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[Candidature]: Le candidature mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        candidature = self.candidature_repository.get_by_id(candidature_id)
        if not candidature:
            return None

        delete_replaced_files(candidature, candidature_data, self.FILE_FIELD_NAMES)
        # Validation des données
        if not partial:
            self.validate_data(candidature_data)

        return self.candidature_repository.update(candidature, **candidature_data)

    def delete(self, candidature_id: int) -> bool:
        """
        Supprimer un candidature.
        
        Args:
            candidature_id (int): L'ID du candidature
            
        Returns:
            bool: True si supprimé avec succès, False si candidature non trouvé
        """
        candidature = self.candidature_repository.get_by_id(candidature_id)
        if not candidature:
            return False

        delete_instance_files(candidature, self.FILE_FIELD_NAMES)
        return self.candidature_repository.delete(candidature)

    def validate_data(self, candidature_data: Dict[str, Any]):
        """
        Valider les données du candidature.
        
        Args:
            candidature_data (Dict[str, Any]): Données du candidature à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        if 'status' in candidature_data:
            _valid_status = ['sent', 'shortlisted', 'rejected', 'accepted']
            if candidature_data['status'] not in _valid_status:
                raise ValidationError("Valeur invalide pour le champ status")
        # Ajoutez d'autres validations selon vos besoins