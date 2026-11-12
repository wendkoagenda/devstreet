"""
Availability repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.marketplace.models import Availability
from app.marketplace.interfaces.availability_repository_interface import AvailabilityRepositoryInterface


class AvailabilityRepository(AvailabilityRepositoryInterface):
    """
    Implémentation concrète des opérations du repository availabilitys.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('status', 'source', 'note',)
    ORDERING_FIELDS = ('id', 'start_date', 'end_date', 'status', 'hours_per_week', 'source', 'note', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les availability, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les availability filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = Availability.objects.all()
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

    def get_by_id(self, availability_id: int) -> Optional[Availability]:
        """
        Obtenir un availability par ID.

        Args:
            availability_id (int): L'ID du availability

        Returns:
            Optional[Availability]: Le availability si trouvé, None sinon
        """
        return Availability.objects.filter(id=availability_id).first()

    def create(self, **kwargs) -> Availability:
        """
        Créer un nouveau availability.

        Args:
            **kwargs: Données du availability

        Returns:
            Availability: Le availability créé
        """
        return Availability.objects.create(**kwargs)

    def update(self, availability: Availability, **kwargs) -> Availability:
        """
        Mettre à jour un availability existant.

        Args:
            availability (Availability): Le availability à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Availability: Le availability mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(availability, field):
                setattr(availability, field, value)

        availability.save()
        return availability

    def delete(self, availability: Availability) -> bool:
        """
        Supprimer un availability.

        Args:
            availability (Availability): Le availability à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        availability.delete()
        return True

    def exists_by_id(self, availability_id: int) -> bool:
        """
        Vérifier si un availability existe par ID.

        Args:
            availability_id (int): L'ID du availability

        Returns:
            bool: True si le availability existe, False sinon
        """
        return Availability.objects.filter(id=availability_id).exists()