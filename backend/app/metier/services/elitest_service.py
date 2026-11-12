"""
Elitest service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.metier.models import Elitest
from app.metier.repositories.elitest_repository import ElitestRepository
from app.metier.utils.file_field_utils import delete_instance_files, delete_replaced_files


class ElitestService:
    """
    Classe de service pour la logique métier liée aux elitests.
    """
    FILE_FIELD_NAMES = ["document"]

    def __init__(self):
        self.elitest_repository = ElitestRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les elitests, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les elitests filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.elitest_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, elitest_id: int) -> Optional[Elitest]:
        """
        Obtenir un elitest par ID.
        
        Args:
            elitest_id (int): L'ID du elitest
            
        Returns:
            Optional[Elitest]: Le elitest si trouvé, None sinon
        """
        return self.elitest_repository.get_by_id(elitest_id)

    def create(self, elitest_data: Dict[str, Any]) -> Elitest:
        """
        Créer un nouveau elitest avec validation.
        
        Args:
            elitest_data (Dict[str, Any]): Données du elitest
            
        Returns:
            Elitest: Le elitest créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(elitest_data)
        
        return self.elitest_repository.create(**elitest_data)

    def update(self, elitest_id: int, elitest_data: Dict[str, Any], partial: bool = False) -> Optional[Elitest]:
        """
        Mettre à jour un elitest existant.
        
        Args:
            elitest_id (int): L'ID du elitest
            elitest_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[Elitest]: Le elitest mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        elitest = self.elitest_repository.get_by_id(elitest_id)
        if not elitest:
            return None

        delete_replaced_files(elitest, elitest_data, self.FILE_FIELD_NAMES)
        # Validation des données
        if not partial:
            self.validate_data(elitest_data)

        return self.elitest_repository.update(elitest, **elitest_data)

    def delete(self, elitest_id: int) -> bool:
        """
        Supprimer un elitest.
        
        Args:
            elitest_id (int): L'ID du elitest
            
        Returns:
            bool: True si supprimé avec succès, False si elitest non trouvé
        """
        elitest = self.elitest_repository.get_by_id(elitest_id)
        if not elitest:
            return False

        delete_instance_files(elitest, self.FILE_FIELD_NAMES)
        return self.elitest_repository.delete(elitest)

    def validate_data(self, elitest_data: Dict[str, Any]):
        """
        Valider les données du elitest.
        
        Args:
            elitest_data (Dict[str, Any]): Données du elitest à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        if 'titre' in elitest_data and not elitest_data['titre'].strip():
            raise ValidationError("Le champ titre ne peut pas être vide")
        if 'statut' in elitest_data and not elitest_data['statut'].strip():
            raise ValidationError("Le champ statut ne peut pas être vide")
        if 'statut' in elitest_data:
            _valid_statut = ['draft', 'published', 'archived']
            if elitest_data['statut'] not in _valid_statut:
                raise ValidationError("Valeur invalide pour le champ statut")
        # Ajoutez d'autres validations selon vos besoins