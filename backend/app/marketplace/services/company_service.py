"""
Company service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.marketplace.models import Company
from app.marketplace.repositories.company_repository import CompanyRepository
from app.metier.utils.file_field_utils import delete_instance_files, delete_replaced_files


class CompanyService:
    """
    Classe de service pour la logique métier liée aux companys.
    """
    FILE_FIELD_NAMES = ["logo"]

    def __init__(self):
        self.company_repository = CompanyRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les companys, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les companys filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.company_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, company_id: int) -> Optional[Company]:
        """
        Obtenir un company par ID.
        
        Args:
            company_id (int): L'ID du company
            
        Returns:
            Optional[Company]: Le company si trouvé, None sinon
        """
        return self.company_repository.get_by_id(company_id)

    def create(self, company_data: Dict[str, Any]) -> Company:
        """
        Créer un nouveau company avec validation.
        
        Args:
            company_data (Dict[str, Any]): Données du company
            
        Returns:
            Company: Le company créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(company_data)
        
        return self.company_repository.create(**company_data)

    def update(self, company_id: int, company_data: Dict[str, Any], partial: bool = False) -> Optional[Company]:
        """
        Mettre à jour un company existant.
        
        Args:
            company_id (int): L'ID du company
            company_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[Company]: Le company mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        company = self.company_repository.get_by_id(company_id)
        if not company:
            return None

        delete_replaced_files(company, company_data, self.FILE_FIELD_NAMES)
        # Validation des données
        if not partial:
            self.validate_data(company_data)

        return self.company_repository.update(company, **company_data)

    def delete(self, company_id: int) -> bool:
        """
        Supprimer un company.
        
        Args:
            company_id (int): L'ID du company
            
        Returns:
            bool: True si supprimé avec succès, False si company non trouvé
        """
        company = self.company_repository.get_by_id(company_id)
        if not company:
            return False

        delete_instance_files(company, self.FILE_FIELD_NAMES)
        return self.company_repository.delete(company)

    def validate_data(self, company_data: Dict[str, Any]):
        """
        Valider les données du company.
        
        Args:
            company_data (Dict[str, Any]): Données du company à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        if 'sector' in company_data:
            _valid_sector = ['fintech', 'ecommerce', 'agritech', 'edtech', 'health', 'ngo', 'public', 'other']
            if company_data['sector'] not in _valid_sector:
                raise ValidationError("Valeur invalide pour le champ sector")
        if 'size' in company_data:
            _valid_size = ['1-10', '11-50', '51-200', '200+']
            if company_data['size'] not in _valid_size:
                raise ValidationError("Valeur invalide pour le champ size")
        # Ajoutez d'autres validations selon vos besoins