"""
Elitesty service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.metier.models import Elitesty
from app.metier.repositories.elitesty_repository import ElitestyRepository
from app.metier.utils.file_field_utils import delete_instance_files, delete_replaced_files


class ElitestyService:
    """
    Classe de service pour la logique métier liée aux elitestys.
    """
    FILE_FIELD_NAMES = ["document"]

    def __init__(self):
        self.elitesty_repository = ElitestyRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les elitestys, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les elitestys filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.elitesty_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, elitesty_id: int) -> Optional[Elitesty]:
        """
        Obtenir un elitesty par ID.
        
        Args:
            elitesty_id (int): L'ID du elitesty
            
        Returns:
            Optional[Elitesty]: Le elitesty si trouvé, None sinon
        """
        return self.elitesty_repository.get_by_id(elitesty_id)

    def create(self, elitesty_data: Dict[str, Any]) -> Elitesty:
        """
        Créer un nouveau elitesty avec validation.
        
        Args:
            elitesty_data (Dict[str, Any]): Données du elitesty
            
        Returns:
            Elitesty: Le elitesty créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(elitesty_data)
        
        return self.elitesty_repository.create(**elitesty_data)

    def update(self, elitesty_id: int, elitesty_data: Dict[str, Any], partial: bool = False) -> Optional[Elitesty]:
        """
        Mettre à jour un elitesty existant.
        
        Args:
            elitesty_id (int): L'ID du elitesty
            elitesty_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[Elitesty]: Le elitesty mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        elitesty = self.elitesty_repository.get_by_id(elitesty_id)
        if not elitesty:
            return None

        delete_replaced_files(elitesty, elitesty_data, self.FILE_FIELD_NAMES)
        # Validation des données
        if not partial:
            self.validate_data(elitesty_data)

        return self.elitesty_repository.update(elitesty, **elitesty_data)

    def delete(self, elitesty_id: int) -> bool:
        """
        Supprimer un elitesty.
        
        Args:
            elitesty_id (int): L'ID du elitesty
            
        Returns:
            bool: True si supprimé avec succès, False si elitesty non trouvé
        """
        elitesty = self.elitesty_repository.get_by_id(elitesty_id)
        if not elitesty:
            return False

        delete_instance_files(elitesty, self.FILE_FIELD_NAMES)
        return self.elitesty_repository.delete(elitesty)

    def validate_data(self, elitesty_data: Dict[str, Any]):
        """
        Valider les données du elitesty.
        
        Args:
            elitesty_data (Dict[str, Any]): Données du elitesty à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        if 'titre' in elitesty_data and not elitesty_data['titre'].strip():
            raise ValidationError("Le champ titre ne peut pas être vide")
        if 'statut' in elitesty_data and not elitesty_data['statut'].strip():
            raise ValidationError("Le champ statut ne peut pas être vide")
        if 'statut' in elitesty_data:
            _valid_statut = ['draft', 'published', 'archived']
            if elitesty_data['statut'] not in _valid_statut:
                raise ValidationError("Valeur invalide pour le champ statut")
        # Ajoutez d'autres validations selon vos besoins