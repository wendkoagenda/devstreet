"""
ProfilHistory service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.marketplace.models import ProfilHistory
from app.marketplace.repositories.profilhistory_repository import ProfilHistoryRepository


class ProfilHistoryService:
    """
    Classe de service pour la logique métier liée aux profil_historys.
    """

    def __init__(self):
        self.profilhistory_repository = ProfilHistoryRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les profil_historys, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les profil_historys filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.profilhistory_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, profil_history_id: int) -> Optional[ProfilHistory]:
        """
        Obtenir un profil_history par ID.
        
        Args:
            profil_history_id (int): L'ID du profil_history
            
        Returns:
            Optional[ProfilHistory]: Le profil_history si trouvé, None sinon
        """
        return self.profilhistory_repository.get_by_id(profil_history_id)

    def create(self, profil_history_data: Dict[str, Any]) -> ProfilHistory:
        """
        Créer un nouveau profil_history avec validation.
        
        Args:
            profil_history_data (Dict[str, Any]): Données du profil_history
            
        Returns:
            ProfilHistory: Le profil_history créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(profil_history_data)
        
        return self.profilhistory_repository.create(**profil_history_data)

    def update(self, profil_history_id: int, profil_history_data: Dict[str, Any], partial: bool = False) -> Optional[ProfilHistory]:
        """
        Mettre à jour un profil_history existant.
        
        Args:
            profil_history_id (int): L'ID du profil_history
            profil_history_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[ProfilHistory]: Le profil_history mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        profil_history = self.profilhistory_repository.get_by_id(profil_history_id)
        if not profil_history:
            return None

        # Validation des données
        if not partial:
            self.validate_data(profil_history_data)

        return self.profilhistory_repository.update(profil_history, **profil_history_data)

    def delete(self, profil_history_id: int) -> bool:
        """
        Supprimer un profil_history.
        
        Args:
            profil_history_id (int): L'ID du profil_history
            
        Returns:
            bool: True si supprimé avec succès, False si profil_history non trouvé
        """
        profil_history = self.profilhistory_repository.get_by_id(profil_history_id)
        if not profil_history:
            return False

        return self.profilhistory_repository.delete(profil_history)

    def validate_data(self, profil_history_data: Dict[str, Any]):
        """
        Valider les données du profil_history.
        
        Args:
            profil_history_data (Dict[str, Any]): Données du profil_history à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        if 'source' in profil_history_data:
            _valid_source = ['manual', 'ai', 'system']
            if profil_history_data['source'] not in _valid_source:
                raise ValidationError("Valeur invalide pour le champ source")
        # Ajoutez d'autres validations selon vos besoins