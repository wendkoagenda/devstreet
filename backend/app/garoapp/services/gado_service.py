"""
Gado service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.garoapp.models import Gado
from app.garoapp.repositories.gado_repository import GadoRepository
from app.metier.utils.file_field_utils import delete_instance_files, delete_replaced_files


class GadoService:
    """
    Classe de service pour la logique métier liée aux gados.
    """
    FILE_FIELD_NAMES = ["document"]

    def __init__(self):
        self.gado_repository = GadoRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les gados, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les gados filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.gado_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, gado_id: int) -> Optional[Gado]:
        """
        Obtenir un gado par ID.
        
        Args:
            gado_id (int): L'ID du gado
            
        Returns:
            Optional[Gado]: Le gado si trouvé, None sinon
        """
        return self.gado_repository.get_by_id(gado_id)

    def create(self, gado_data: Dict[str, Any]) -> Gado:
        """
        Créer un nouveau gado avec validation.
        
        Args:
            gado_data (Dict[str, Any]): Données du gado
            
        Returns:
            Gado: Le gado créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(gado_data)
        
        return self.gado_repository.create(**gado_data)

    def update(self, gado_id: int, gado_data: Dict[str, Any], partial: bool = False) -> Optional[Gado]:
        """
        Mettre à jour un gado existant.
        
        Args:
            gado_id (int): L'ID du gado
            gado_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[Gado]: Le gado mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        gado = self.gado_repository.get_by_id(gado_id)
        if not gado:
            return None

        delete_replaced_files(gado, gado_data, self.FILE_FIELD_NAMES)
        # Validation des données
        if not partial:
            self.validate_data(gado_data)

        return self.gado_repository.update(gado, **gado_data)

    def delete(self, gado_id: int) -> bool:
        """
        Supprimer un gado.
        
        Args:
            gado_id (int): L'ID du gado
            
        Returns:
            bool: True si supprimé avec succès, False si gado non trouvé
        """
        gado = self.gado_repository.get_by_id(gado_id)
        if not gado:
            return False

        delete_instance_files(gado, self.FILE_FIELD_NAMES)
        return self.gado_repository.delete(gado)

    def validate_data(self, gado_data: Dict[str, Any]):
        """
        Valider les données du gado.
        
        Args:
            gado_data (Dict[str, Any]): Données du gado à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        if 'titre' in gado_data and not gado_data['titre'].strip():
            raise ValidationError("Le champ titre ne peut pas être vide")
        if 'statut' in gado_data and not gado_data['statut'].strip():
            raise ValidationError("Le champ statut ne peut pas être vide")
        if 'statut' in gado_data:
            _valid_statut = ['draft', 'published', 'archived']
            if gado_data['statut'] not in _valid_statut:
                raise ValidationError("Valeur invalide pour le champ statut")
        # Ajoutez d'autres validations selon vos besoins