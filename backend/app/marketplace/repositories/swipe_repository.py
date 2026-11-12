"""
Swipe repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.marketplace.models import Swipe
from app.marketplace.interfaces.swipe_repository_interface import SwipeRepositoryInterface


class SwipeRepository(SwipeRepositoryInterface):
    """
    Implémentation concrète des opérations du repository swipes.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('direction', 'context',)
    ORDERING_FIELDS = ('id', 'direction', 'context', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les swipe, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les swipe filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = Swipe.objects.all()
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

    def get_by_id(self, swipe_id: int) -> Optional[Swipe]:
        """
        Obtenir un swipe par ID.

        Args:
            swipe_id (int): L'ID du swipe

        Returns:
            Optional[Swipe]: Le swipe si trouvé, None sinon
        """
        return Swipe.objects.filter(id=swipe_id).first()

    def create(self, **kwargs) -> Swipe:
        """
        Créer un nouveau swipe.

        Args:
            **kwargs: Données du swipe

        Returns:
            Swipe: Le swipe créé
        """
        return Swipe.objects.create(**kwargs)

    def update(self, swipe: Swipe, **kwargs) -> Swipe:
        """
        Mettre à jour un swipe existant.

        Args:
            swipe (Swipe): Le swipe à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Swipe: Le swipe mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(swipe, field):
                setattr(swipe, field, value)

        swipe.save()
        return swipe

    def delete(self, swipe: Swipe) -> bool:
        """
        Supprimer un swipe.

        Args:
            swipe (Swipe): Le swipe à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        swipe.delete()
        return True

    def exists_by_id(self, swipe_id: int) -> bool:
        """
        Vérifier si un swipe existe par ID.

        Args:
            swipe_id (int): L'ID du swipe

        Returns:
            bool: True si le swipe existe, False sinon
        """
        return Swipe.objects.filter(id=swipe_id).exists()