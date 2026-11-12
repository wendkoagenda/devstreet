"""
Experience service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.marketplace.models import Experience
from app.marketplace.repositories.experience_repository import ExperienceRepository


class ExperienceService:
    """
    Classe de service pour la logique métier liée aux experiences.
    """

    def __init__(self):
        self.experience_repository = ExperienceRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les experiences, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les experiences filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.experience_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, experience_id: int) -> Optional[Experience]:
        """
        Obtenir un experience par ID.
        
        Args:
            experience_id (int): L'ID du experience
            
        Returns:
            Optional[Experience]: Le experience si trouvé, None sinon
        """
        return self.experience_repository.get_by_id(experience_id)

    def create(self, experience_data: Dict[str, Any]) -> Experience:
        """
        Créer un nouveau experience avec validation.
        
        Args:
            experience_data (Dict[str, Any]): Données du experience
            
        Returns:
            Experience: Le experience créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(experience_data)
        
        return self.experience_repository.create(**experience_data)

    def update(self, experience_id: int, experience_data: Dict[str, Any], partial: bool = False) -> Optional[Experience]:
        """
        Mettre à jour un experience existant.
        
        Args:
            experience_id (int): L'ID du experience
            experience_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[Experience]: Le experience mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        experience = self.experience_repository.get_by_id(experience_id)
        if not experience:
            return None

        # Validation des données
        if not partial:
            self.validate_data(experience_data)

        return self.experience_repository.update(experience, **experience_data)

    def delete(self, experience_id: int) -> bool:
        """
        Supprimer un experience.
        
        Args:
            experience_id (int): L'ID du experience
            
        Returns:
            bool: True si supprimé avec succès, False si experience non trouvé
        """
        experience = self.experience_repository.get_by_id(experience_id)
        if not experience:
            return False

        return self.experience_repository.delete(experience)

    def validate_data(self, experience_data: Dict[str, Any]):
        """
        Valider les données du experience.
        
        Args:
            experience_data (Dict[str, Any]): Données du experience à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        if 'contract_type' in experience_data:
            _valid_contract_type = ['cdi', 'cdd', 'freelance', 'stage']
            if experience_data['contract_type'] not in _valid_contract_type:
                raise ValidationError("Valeur invalide pour le champ contract_type")
        # Ajoutez d'autres validations selon vos besoins