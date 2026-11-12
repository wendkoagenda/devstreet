"""
ProfilSkill service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.marketplace.models import ProfilSkill
from app.marketplace.repositories.profilskill_repository import ProfilSkillRepository


class ProfilSkillService:
    """
    Classe de service pour la logique métier liée aux profil_skills.
    """

    def __init__(self):
        self.profilskill_repository = ProfilSkillRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les profil_skills, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les profil_skills filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.profilskill_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, profil_skill_id: int) -> Optional[ProfilSkill]:
        """
        Obtenir un profil_skill par ID.
        
        Args:
            profil_skill_id (int): L'ID du profil_skill
            
        Returns:
            Optional[ProfilSkill]: Le profil_skill si trouvé, None sinon
        """
        return self.profilskill_repository.get_by_id(profil_skill_id)

    def create(self, profil_skill_data: Dict[str, Any]) -> ProfilSkill:
        """
        Créer un nouveau profil_skill avec validation.
        
        Args:
            profil_skill_data (Dict[str, Any]): Données du profil_skill
            
        Returns:
            ProfilSkill: Le profil_skill créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(profil_skill_data)
        
        return self.profilskill_repository.create(**profil_skill_data)

    def update(self, profil_skill_id: int, profil_skill_data: Dict[str, Any], partial: bool = False) -> Optional[ProfilSkill]:
        """
        Mettre à jour un profil_skill existant.
        
        Args:
            profil_skill_id (int): L'ID du profil_skill
            profil_skill_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[ProfilSkill]: Le profil_skill mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        profil_skill = self.profilskill_repository.get_by_id(profil_skill_id)
        if not profil_skill:
            return None

        # Validation des données
        if not partial:
            self.validate_data(profil_skill_data)

        return self.profilskill_repository.update(profil_skill, **profil_skill_data)

    def delete(self, profil_skill_id: int) -> bool:
        """
        Supprimer un profil_skill.
        
        Args:
            profil_skill_id (int): L'ID du profil_skill
            
        Returns:
            bool: True si supprimé avec succès, False si profil_skill non trouvé
        """
        profil_skill = self.profilskill_repository.get_by_id(profil_skill_id)
        if not profil_skill:
            return False

        return self.profilskill_repository.delete(profil_skill)

    def validate_data(self, profil_skill_data: Dict[str, Any]):
        """
        Valider les données du profil_skill.
        
        Args:
            profil_skill_data (Dict[str, Any]): Données du profil_skill à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        # Ajoutez d'autres validations selon vos besoins