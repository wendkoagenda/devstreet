"""
Project repository implementation pour les opérations d'accès aux données.
"""

from typing import Optional
from django.db.models import QuerySet, Q
from app.projects.models import Project
from app.projects.interfaces.project_repository_interface import (
    ProjectRepositoryInterface,
)


class ProjectRepository(ProjectRepositoryInterface):
    """
    Implémentation concrète des opérations du repository projects.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = (
        "title",
        "slug",
        "problem",
        "description",
        "demo_url",
        "declared_license",
        "status",
    )
    ORDERING_FIELDS = (
        "id",
        "title",
        "slug",
        "problem",
        "description",
        "demo_url",
        "declared_license",
        "status",
        "created_at",
        "updated_at",
    )

    def get_all(
        self, search: Optional[str] = None, ordering: Optional[str] = None
    ) -> QuerySet:
        """
        Obtenir les project, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les project filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = Project.objects.all()
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

    def get_by_id(self, project_id: int) -> Optional[Project]:
        """
        Obtenir un project par ID.

        Args:
            project_id (int): L'ID du project

        Returns:
            Optional[Project]: Le project si trouvé, None sinon
        """
        return Project.objects.filter(id=project_id).first()

    def create(self, **kwargs) -> Project:
        """
        Créer un nouveau project.

        Args:
            **kwargs: Données du project

        Returns:
            Project: Le project créé
        """
        return Project.objects.create(**kwargs)

    def update(self, project: Project, **kwargs) -> Project:
        """
        Mettre à jour un project existant.

        Args:
            project (Project): Le project à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Project: Le project mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(project, field):
                setattr(project, field, value)

        project.save()
        return project

    def delete(self, project: Project) -> bool:
        """
        Supprimer un project.

        Args:
            project (Project): Le project à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        project.delete()
        return True

    def exists_by_id(self, project_id: int) -> bool:
        """
        Vérifier si un project existe par ID.

        Args:
            project_id (int): L'ID du project

        Returns:
            bool: True si le project existe, False sinon
        """
        return Project.objects.filter(id=project_id).exists()
