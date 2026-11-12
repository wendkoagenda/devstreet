"""
NotificationResume service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from app.communaute.models import NotificationResume
from app.communaute.repositories.notificationresume_repository import NotificationResumeRepository


class NotificationResumeService:
    """
    Classe de service pour la logique métier liée aux notification_resumes.
    """

    def __init__(self):
        self.notificationresume_repository = NotificationResumeRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les notification_resumes, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les notification_resumes filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.notificationresume_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, notification_resume_id: int) -> Optional[NotificationResume]:
        """
        Obtenir un notification_resume par ID.
        
        Args:
            notification_resume_id (int): L'ID du notification_resume
            
        Returns:
            Optional[NotificationResume]: Le notification_resume si trouvé, None sinon
        """
        return self.notificationresume_repository.get_by_id(notification_resume_id)

    def create(self, notification_resume_data: Dict[str, Any]) -> NotificationResume:
        """
        Créer un nouveau notification_resume avec validation.
        
        Args:
            notification_resume_data (Dict[str, Any]): Données du notification_resume
            
        Returns:
            NotificationResume: Le notification_resume créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(notification_resume_data)
        
        return self.notificationresume_repository.create(**notification_resume_data)

    def update(self, notification_resume_id: int, notification_resume_data: Dict[str, Any], partial: bool = False) -> Optional[NotificationResume]:
        """
        Mettre à jour un notification_resume existant.
        
        Args:
            notification_resume_id (int): L'ID du notification_resume
            notification_resume_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[NotificationResume]: Le notification_resume mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        notification_resume = self.notificationresume_repository.get_by_id(notification_resume_id)
        if not notification_resume:
            return None

        # Validation des données
        if not partial:
            self.validate_data(notification_resume_data)

        return self.notificationresume_repository.update(notification_resume, **notification_resume_data)

    def delete(self, notification_resume_id: int) -> bool:
        """
        Supprimer un notification_resume.
        
        Args:
            notification_resume_id (int): L'ID du notification_resume
            
        Returns:
            bool: True si supprimé avec succès, False si notification_resume non trouvé
        """
        notification_resume = self.notificationresume_repository.get_by_id(notification_resume_id)
        if not notification_resume:
            return False

        return self.notificationresume_repository.delete(notification_resume)

    def validate_data(self, notification_resume_data: Dict[str, Any]):
        """
        Valider les données du notification_resume.
        
        Args:
            notification_resume_data (Dict[str, Any]): Données du notification_resume à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        # Ajoutez d'autres validations selon vos besoins