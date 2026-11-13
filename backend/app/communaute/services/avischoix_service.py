"""
AvisChoix service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.communaute.models import AvisChoix
from app.communaute.repositories.avischoix_repository import AvisChoixRepository


class AvisChoixService:
    """
    Classe de service pour la logique métier liée aux avis_choixs.
    """

    def __init__(self):
        self.avischoix_repository = AvisChoixRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les avis_choixs, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les avis_choixs filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.avischoix_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, avis_choix_id: int) -> Optional[AvisChoix]:
        """
        Obtenir un avis_choix par ID.
        
        Args:
            avis_choix_id (int): L'ID du avis_choix
            
        Returns:
            Optional[AvisChoix]: Le avis_choix si trouvé, None sinon
        """
        return self.avischoix_repository.get_by_id(avis_choix_id)

    def create(self, avis_choix_data: Dict[str, Any]) -> AvisChoix:
        """
        Créer un nouveau avis_choix avec validation.
        
        Args:
            avis_choix_data (Dict[str, Any]): Données du avis_choix
            
        Returns:
            AvisChoix: Le avis_choix créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(avis_choix_data)
        
        return self.avischoix_repository.create(**avis_choix_data)

    def update(self, avis_choix_id: int, avis_choix_data: Dict[str, Any], partial: bool = False) -> Optional[AvisChoix]:
        """
        Mettre à jour un avis_choix existant.
        
        Args:
            avis_choix_id (int): L'ID du avis_choix
            avis_choix_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[AvisChoix]: Le avis_choix mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        avis_choix = self.avischoix_repository.get_by_id(avis_choix_id)
        if not avis_choix:
            return None

        # Validation des données
        if not partial:
            self.validate_data(avis_choix_data)

        return self.avischoix_repository.update(avis_choix, **avis_choix_data)

    def delete(self, avis_choix_id: int) -> bool:
        """
        Supprimer un avis_choix.
        
        Args:
            avis_choix_id (int): L'ID du avis_choix
            
        Returns:
            bool: True si supprimé avec succès, False si avis_choix non trouvé
        """
        avis_choix = self.avischoix_repository.get_by_id(avis_choix_id)
        if not avis_choix:
            return False

        return self.avischoix_repository.delete(avis_choix)

    def validate_data(self, avis_choix_data: Dict[str, Any]):
        """
        Valider les données du avis_choix.
        
        Args:
            avis_choix_data (Dict[str, Any]): Données du avis_choix à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        # Ajoutez d'autres validations selon vos besoins