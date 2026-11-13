"""
NotificationResume repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.communaute.models import NotificationResume
from app.communaute.interfaces.notificationresume_repository_interface import NotificationResumeRepositoryInterface


class NotificationResumeRepository(NotificationResumeRepositoryInterface):
    """
    Implémentation concrète des opérations du repository notificationresumes.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ()
    ORDERING_FIELDS = ('id', 'periode_debut', 'periode_fin', 'nombre_nouveautes', 'read_at', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les notification_resume, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les notification_resume filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = NotificationResume.objects.all()
        if search:
            condition = Q()
            for field_name in self.SEARCH_FIELDS:
                condition |= Q(**{f'{field_name}__icontains': search})
            queryset = queryset.filter(condition)
        if ordering:
            if ordering.lstrip('-') not in self.ORDERING_FIELDS:
                raise ValueError(f'Tri non autorisé : {ordering}')
            return queryset.order_by(ordering, 'id')
        return queryset.order_by('id')

    def get_by_id(self, notification_resume_id: int) -> Optional[NotificationResume]:
        """
        Obtenir un notification_resume par ID.

        Args:
            notification_resume_id (int): L'ID du notification_resume

        Returns:
            Optional[NotificationResume]: Le notification_resume si trouvé, None sinon
        """
        return NotificationResume.objects.filter(id=notification_resume_id).first()

    def create(self, **kwargs) -> NotificationResume:
        """
        Créer un nouveau notification_resume.

        Args:
            **kwargs: Données du notification_resume

        Returns:
            NotificationResume: Le notification_resume créé
        """
        return NotificationResume.objects.create(**kwargs)

    def update(self, notification_resume: NotificationResume, **kwargs) -> NotificationResume:
        """
        Mettre à jour un notification_resume existant.

        Args:
            notification_resume (NotificationResume): Le notification_resume à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            NotificationResume: Le notification_resume mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(notification_resume, field):
                setattr(notification_resume, field, value)

        notification_resume.save()
        return notification_resume

    def delete(self, notification_resume: NotificationResume) -> bool:
        """
        Supprimer un notification_resume.

        Args:
            notification_resume (NotificationResume): Le notification_resume à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        notification_resume.delete()
        return True

    def exists_by_id(self, notification_resume_id: int) -> bool:
        """
        Vérifier si un notification_resume existe par ID.

        Args:
            notification_resume_id (int): L'ID du notification_resume

        Returns:
            bool: True si le notification_resume existe, False sinon
        """
        return NotificationResume.objects.filter(id=notification_resume_id).exists()