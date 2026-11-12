"""
Prestation repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.marketplace.models import Prestation
from app.marketplace.interfaces.prestation_repository_interface import PrestationRepositoryInterface


class PrestationRepository(PrestationRepositoryInterface):
    """
    Implémentation concrète des opérations du repository prestations.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('title', 'slug', 'description', 'category', 'currency',)
    ORDERING_FIELDS = ('id', 'title', 'slug', 'description', 'category', 'price', 'currency', 'delivery_days', 'revisions', 'cover_image', 'is_active', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les prestation, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les prestation filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = Prestation.objects.all()
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

    def get_by_id(self, prestation_id: int) -> Optional[Prestation]:
        """
        Obtenir un prestation par ID.

        Args:
            prestation_id (int): L'ID du prestation

        Returns:
            Optional[Prestation]: Le prestation si trouvé, None sinon
        """
        return Prestation.objects.filter(id=prestation_id).first()

    def create(self, **kwargs) -> Prestation:
        """
        Créer un nouveau prestation.

        Args:
            **kwargs: Données du prestation

        Returns:
            Prestation: Le prestation créé
        """
        return Prestation.objects.create(**kwargs)

    def update(self, prestation: Prestation, **kwargs) -> Prestation:
        """
        Mettre à jour un prestation existant.

        Args:
            prestation (Prestation): Le prestation à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Prestation: Le prestation mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(prestation, field):
                setattr(prestation, field, value)

        prestation.save()
        return prestation

    def delete(self, prestation: Prestation) -> bool:
        """
        Supprimer un prestation.

        Args:
            prestation (Prestation): Le prestation à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        prestation.delete()
        return True

    def exists_by_id(self, prestation_id: int) -> bool:
        """
        Vérifier si un prestation existe par ID.

        Args:
            prestation_id (int): L'ID du prestation

        Returns:
            bool: True si le prestation existe, False sinon
        """
        return Prestation.objects.filter(id=prestation_id).exists()