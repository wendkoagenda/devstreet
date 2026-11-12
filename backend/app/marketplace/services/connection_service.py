"""
Connection service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.marketplace.models import Connection
from app.marketplace.repositories.connection_repository import ConnectionRepository


class ConnectionService:
    """
    Classe de service pour la logique métier liée aux connections.
    """

    def __init__(self):
        self.connection_repository = ConnectionRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les connections, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les connections filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.connection_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, connection_id: int) -> Optional[Connection]:
        """
        Obtenir un connection par ID.
        
        Args:
            connection_id (int): L'ID du connection
            
        Returns:
            Optional[Connection]: Le connection si trouvé, None sinon
        """
        return self.connection_repository.get_by_id(connection_id)

    def create(self, connection_data: Dict[str, Any]) -> Connection:
        """
        Créer un nouveau connection avec validation.
        
        Args:
            connection_data (Dict[str, Any]): Données du connection
            
        Returns:
            Connection: Le connection créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(connection_data)
        
        return self.connection_repository.create(**connection_data)

    def update(self, connection_id: int, connection_data: Dict[str, Any], partial: bool = False) -> Optional[Connection]:
        """
        Mettre à jour un connection existant.
        
        Args:
            connection_id (int): L'ID du connection
            connection_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[Connection]: Le connection mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        connection = self.connection_repository.get_by_id(connection_id)
        if not connection:
            return None

        # Validation des données
        if not partial:
            self.validate_data(connection_data)

        return self.connection_repository.update(connection, **connection_data)

    def delete(self, connection_id: int) -> bool:
        """
        Supprimer un connection.
        
        Args:
            connection_id (int): L'ID du connection
            
        Returns:
            bool: True si supprimé avec succès, False si connection non trouvé
        """
        connection = self.connection_repository.get_by_id(connection_id)
        if not connection:
            return False

        return self.connection_repository.delete(connection)

    def validate_data(self, connection_data: Dict[str, Any]):
        """
        Valider les données du connection.
        
        Args:
            connection_data (Dict[str, Any]): Données du connection à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        if 'status' in connection_data:
            _valid_status = ['matched', 'blocked']
            if connection_data['status'] not in _valid_status:
                raise ValidationError("Valeur invalide pour le champ status")
        # Ajoutez d'autres validations selon vos besoins