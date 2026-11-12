"""
ProfilSkill repository interface définissant le contrat pour l'accès aux données profilskills.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from django.db.models import QuerySet
from app.marketplace.models import ProfilSkill


class ProfilSkillRepositoryInterface(ABC):
    """
    Interface abstraite pour les opérations du repository profilskills.
    """

    @abstractmethod
    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les profil_skill, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les profil_skill filtrés et triés
        """
        pass

    @abstractmethod
    def get_by_id(self, profil_skill_id: int) -> Optional[ProfilSkill]:
        """
        Obtenir un profil_skill par ID.

        Args:
            profil_skill_id (int): L'ID du profil_skill

        Returns:
            Optional[ProfilSkill]: Le profil_skill si trouvé, None sinon
        """
        pass

    @abstractmethod
    def create(self, **kwargs) -> ProfilSkill:
        """
        Créer un nouveau profil_skill.

        Args:
            **kwargs: Données du profil_skill

        Returns:
            ProfilSkill: Le profil_skill créé
        """
        pass

    @abstractmethod
    def update(self, profil_skill: ProfilSkill, **kwargs) -> ProfilSkill:
        """
        Mettre à jour un profil_skill existant.

        Args:
            profil_skill (ProfilSkill): Le profil_skill à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            ProfilSkill: Le profil_skill mis à jour
        """
        pass

    @abstractmethod
    def delete(self, profil_skill: ProfilSkill) -> bool:
        """
        Supprimer un profil_skill.

        Args:
            profil_skill (ProfilSkill): Le profil_skill à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        pass

    @abstractmethod
    def exists_by_id(self, profil_skill_id: int) -> bool:
        """
        Vérifier si un profil_skill existe par ID.

        Args:
            profil_skill_id (int): L'ID du profil_skill

        Returns:
            bool: True si le profil_skill existe, False sinon
        """
        pass