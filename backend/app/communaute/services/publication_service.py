"""
Publication service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.communaute.models import Publication
from app.communaute.repositories.publication_repository import PublicationRepository


class PublicationService:
    """
    Classe de service pour la logique métier liée aux publications.
    """

    def __init__(self):
        self.publication_repository = PublicationRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les publications, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les publications filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.publication_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, publication_id: int) -> Optional[Publication]:
        """
        Obtenir un publication par ID.
        
        Args:
            publication_id (int): L'ID du publication
            
        Returns:
            Optional[Publication]: Le publication si trouvé, None sinon
        """
        return self.publication_repository.get_by_id(publication_id)

    def create(self, publication_data: Dict[str, Any]) -> Publication:
        """
        Créer un nouveau publication avec validation.
        
        Args:
            publication_data (Dict[str, Any]): Données du publication
            
        Returns:
            Publication: Le publication créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(publication_data)
        
        return self.publication_repository.create(**publication_data)

    def update(self, publication_id: int, publication_data: Dict[str, Any], partial: bool = False) -> Optional[Publication]:
        """
        Mettre à jour un publication existant.
        
        Args:
            publication_id (int): L'ID du publication
            publication_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[Publication]: Le publication mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        publication = self.publication_repository.get_by_id(publication_id)
        if not publication:
            return None

        # Validation des données
        if not partial:
            self.validate_data(publication_data)

        return self.publication_repository.update(publication, **publication_data)

    def delete(self, publication_id: int) -> bool:
        """
        Supprimer un publication.
        
        Args:
            publication_id (int): L'ID du publication
            
        Returns:
            bool: True si supprimé avec succès, False si publication non trouvé
        """
        publication = self.publication_repository.get_by_id(publication_id)
        if not publication:
            return False

        return self.publication_repository.delete(publication)

    def validate_data(self, publication_data: Dict[str, Any]):
        """
        Valider les données du publication.
        
        Args:
            publication_data (Dict[str, Any]): Données du publication à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        if 'type' in publication_data:
            _valid_type = ['DISCUSSION', 'APPLICATION', 'ENTRAIDE', 'CHOIX', 'SONDAGE']
            if publication_data['type'] not in _valid_type:
                raise ValidationError("Valeur invalide pour le champ type")
        if 'plateforme_app' in publication_data:
            _valid_plateforme_app = ['WEB', 'MOBILE', 'LES_DEUX']
            if publication_data['plateforme_app'] not in _valid_plateforme_app:
                raise ValidationError("Valeur invalide pour le champ plateforme_app")
        if 'mode_vote' in publication_data:
            _valid_mode_vote = ['UNIQUE', 'MULTIPLE']
            if publication_data['mode_vote'] not in _valid_mode_vote:
                raise ValidationError("Valeur invalide pour le champ mode_vote")
        # Ajoutez d'autres validations selon vos besoins