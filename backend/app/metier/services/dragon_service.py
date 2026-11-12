"""
Dragon service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.metier.models import Dragon
from app.metier.repositories.dragon_repository import DragonRepository
from app.metier.utils.file_field_utils import delete_instance_files, delete_replaced_files


class DragonService:
    """
    Classe de service pour la logique métier liée aux dragons.
    """
    FILE_FIELD_NAMES = ["document"]

    def __init__(self):
        self.dragon_repository = DragonRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les dragons, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les dragons filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.dragon_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, dragon_id: int) -> Optional[Dragon]:
        """
        Obtenir un dragon par ID.
        
        Args:
            dragon_id (int): L'ID du dragon
            
        Returns:
            Optional[Dragon]: Le dragon si trouvé, None sinon
        """
        return self.dragon_repository.get_by_id(dragon_id)

    def create(self, dragon_data: Dict[str, Any]) -> Dragon:
        """
        Créer un nouveau dragon avec validation.
        
        Args:
            dragon_data (Dict[str, Any]): Données du dragon
            
        Returns:
            Dragon: Le dragon créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(dragon_data)
        
        return self.dragon_repository.create(**dragon_data)

    def update(self, dragon_id: int, dragon_data: Dict[str, Any], partial: bool = False) -> Optional[Dragon]:
        """
        Mettre à jour un dragon existant.
        
        Args:
            dragon_id (int): L'ID du dragon
            dragon_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[Dragon]: Le dragon mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        dragon = self.dragon_repository.get_by_id(dragon_id)
        if not dragon:
            return None

        delete_replaced_files(dragon, dragon_data, self.FILE_FIELD_NAMES)
        # Validation des données
        if not partial:
            self.validate_data(dragon_data)

        return self.dragon_repository.update(dragon, **dragon_data)

    def delete(self, dragon_id: int) -> bool:
        """
        Supprimer un dragon.
        
        Args:
            dragon_id (int): L'ID du dragon
            
        Returns:
            bool: True si supprimé avec succès, False si dragon non trouvé
        """
        dragon = self.dragon_repository.get_by_id(dragon_id)
        if not dragon:
            return False

        delete_instance_files(dragon, self.FILE_FIELD_NAMES)
        return self.dragon_repository.delete(dragon)

    def validate_data(self, dragon_data: Dict[str, Any]):
        """
        Valider les données du dragon.
        
        Args:
            dragon_data (Dict[str, Any]): Données du dragon à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        if 'titre' in dragon_data and not dragon_data['titre'].strip():
            raise ValidationError("Le champ titre ne peut pas être vide")
        if 'statut' in dragon_data and not dragon_data['statut'].strip():
            raise ValidationError("Le champ statut ne peut pas être vide")
        if 'statut' in dragon_data:
            _valid_statut = ['draft', 'published', 'archived']
            if dragon_data['statut'] not in _valid_statut:
                raise ValidationError("Valeur invalide pour le champ statut")
        # Ajoutez d'autres validations selon vos besoins