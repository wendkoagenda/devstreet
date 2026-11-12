"""
Skill service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.marketplace.models import Skill
from app.marketplace.repositories.skill_repository import SkillRepository


class SkillService:
    """
    Classe de service pour la logique métier liée aux skills.
    """

    def __init__(self):
        self.skill_repository = SkillRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les skills, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les skills filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.skill_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, skill_id: int) -> Optional[Skill]:
        """
        Obtenir un skill par ID.
        
        Args:
            skill_id (int): L'ID du skill
            
        Returns:
            Optional[Skill]: Le skill si trouvé, None sinon
        """
        return self.skill_repository.get_by_id(skill_id)

    def create(self, skill_data: Dict[str, Any]) -> Skill:
        """
        Créer un nouveau skill avec validation.
        
        Args:
            skill_data (Dict[str, Any]): Données du skill
            
        Returns:
            Skill: Le skill créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(skill_data)
        
        return self.skill_repository.create(**skill_data)

    def update(self, skill_id: int, skill_data: Dict[str, Any], partial: bool = False) -> Optional[Skill]:
        """
        Mettre à jour un skill existant.
        
        Args:
            skill_id (int): L'ID du skill
            skill_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[Skill]: Le skill mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        skill = self.skill_repository.get_by_id(skill_id)
        if not skill:
            return None

        # Validation des données
        if not partial:
            self.validate_data(skill_data)

        return self.skill_repository.update(skill, **skill_data)

    def delete(self, skill_id: int) -> bool:
        """
        Supprimer un skill.
        
        Args:
            skill_id (int): L'ID du skill
            
        Returns:
            bool: True si supprimé avec succès, False si skill non trouvé
        """
        skill = self.skill_repository.get_by_id(skill_id)
        if not skill:
            return False

        return self.skill_repository.delete(skill)

    def validate_data(self, skill_data: Dict[str, Any]):
        """
        Valider les données du skill.
        
        Args:
            skill_data (Dict[str, Any]): Données du skill à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        if 'type' in skill_data:
            _valid_type = ['hard', 'soft']
            if skill_data['type'] not in _valid_type:
                raise ValidationError("Valeur invalide pour le champ type")
        if 'category' in skill_data:
            _valid_category = ['frontend', 'backend', 'mobile', 'devops', 'data', 'design', 'management', 'soft']
            if skill_data['category'] not in _valid_category:
                raise ValidationError("Valeur invalide pour le champ category")
        # Ajoutez d'autres validations selon vos besoins