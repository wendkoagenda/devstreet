"""
Technology repository implementation pour les opérations d'accès aux données.
"""

from typing import Optional
from django.db.models import QuerySet, Q
from app.devstreet_hub.models import Technology
from app.devstreet_hub.interfaces.technology_repository_interface import (
    TechnologyRepositoryInterface,
)


class TechnologyRepository(TechnologyRepositoryInterface):
    """
    Implémentation concrète des opérations du repository technologys.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = (
        "label",
        "slug",
    )
    ORDERING_FIELDS = (
        "id",
        "label",
        "slug",
        "created_at",
        "updated_at",
    )

    def get_all(
        self, search: Optional[str] = None, ordering: Optional[str] = None
    ) -> QuerySet:
        """
        Obtenir les technology, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les technology filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = Technology.objects.all()
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

    def get_by_id(self, technology_id: int) -> Optional[Technology]:
        """
        Obtenir un technology par ID.

        Args:
            technology_id (int): L'ID du technology

        Returns:
            Optional[Technology]: Le technology si trouvé, None sinon
        """
        return Technology.objects.filter(id=technology_id).first()

    def create(self, **kwargs) -> Technology:
        """
        Créer un nouveau technology.

        Args:
            **kwargs: Données du technology

        Returns:
            Technology: Le technology créé
        """
        return Technology.objects.create(**kwargs)

    def update(self, technology: Technology, **kwargs) -> Technology:
        """
        Mettre à jour un technology existant.

        Args:
            technology (Technology): Le technology à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Technology: Le technology mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(technology, field):
                setattr(technology, field, value)

        technology.save()
        return technology

    def delete(self, technology: Technology) -> bool:
        """
        Supprimer un technology.

        Args:
            technology (Technology): Le technology à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        technology.delete()
        return True

    def exists_by_id(self, technology_id: int) -> bool:
        """
        Vérifier si un technology existe par ID.

        Args:
            technology_id (int): L'ID du technology

        Returns:
            bool: True si le technology existe, False sinon
        """
        return Technology.objects.filter(id=technology_id).exists()
