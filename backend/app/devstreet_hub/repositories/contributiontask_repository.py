"""
ContributionTask repository implementation pour les opérations d'accès aux données.
"""

from typing import Optional
from django.db.models import QuerySet, Q
from app.devstreet_hub.models import ContributionTask
from app.devstreet_hub.interfaces.contributiontask_repository_interface import (
    ContributionTaskRepositoryInterface,
)


class ContributionTaskRepository(ContributionTaskRepositoryInterface):
    """
    Implémentation concrète des opérations du repository contributiontasks.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = (
        "title",
        "description",
        "status",
    )
    ORDERING_FIELDS = (
        "id",
        "title",
        "description",
        "status",
        "created_at",
        "updated_at",
    )

    def get_all(
        self, search: Optional[str] = None, ordering: Optional[str] = None
    ) -> QuerySet:
        """
        Obtenir les contribution_task, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les contribution_task filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = ContributionTask.objects.all()
        if search:
            condition = Q()
            for field_name in self.SEARCH_FIELDS:
                condition |= Q(**{f"{field_name}__icontains": search})
            queryset = queryset.filter(condition)
        if ordering:
            if ordering.lstrip("-") not in self.ORDERING_FIELDS:
                raise ValueError(f"Tri non autorisé : {ordering}")
            return queryset.order_by(ordering, "id")
        return queryset.order_by("id")

    def get_by_id(self, contribution_task_id: int) -> Optional[ContributionTask]:
        """
        Obtenir un contribution_task par ID.

        Args:
            contribution_task_id (int): L'ID du contribution_task

        Returns:
            Optional[ContributionTask]: Le contribution_task si trouvé, None sinon
        """
        return ContributionTask.objects.filter(id=contribution_task_id).first()

    def create(self, **kwargs) -> ContributionTask:
        """
        Créer un nouveau contribution_task.

        Args:
            **kwargs: Données du contribution_task

        Returns:
            ContributionTask: Le contribution_task créé
        """
        return ContributionTask.objects.create(**kwargs)

    def update(self, contribution_task: ContributionTask, **kwargs) -> ContributionTask:
        """
        Mettre à jour un contribution_task existant.

        Args:
            contribution_task (ContributionTask): Le contribution_task à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            ContributionTask: Le contribution_task mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(contribution_task, field):
                setattr(contribution_task, field, value)

        contribution_task.save()
        return contribution_task

    def delete(self, contribution_task: ContributionTask) -> bool:
        """
        Supprimer un contribution_task.

        Args:
            contribution_task (ContributionTask): Le contribution_task à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        contribution_task.delete()
        return True

    def exists_by_id(self, contribution_task_id: int) -> bool:
        """
        Vérifier si un contribution_task existe par ID.

        Args:
            contribution_task_id (int): L'ID du contribution_task

        Returns:
            bool: True si le contribution_task existe, False sinon
        """
        return ContributionTask.objects.filter(id=contribution_task_id).exists()
