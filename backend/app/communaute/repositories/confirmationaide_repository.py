"""
ConfirmationAide repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.communaute.models import ConfirmationAide
from app.communaute.interfaces.confirmationaide_repository_interface import ConfirmationAideRepositoryInterface


class ConfirmationAideRepository(ConfirmationAideRepositoryInterface):
    """
    Implémentation concrète des opérations du repository confirmationaides.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ()
    ORDERING_FIELDS = ('id', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les confirmation_aide, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les confirmation_aide filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = ConfirmationAide.objects.all()
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

    def get_by_id(self, confirmation_aide_id: int) -> Optional[ConfirmationAide]:
        """
        Obtenir un confirmation_aide par ID.

        Args:
            confirmation_aide_id (int): L'ID du confirmation_aide

        Returns:
            Optional[ConfirmationAide]: Le confirmation_aide si trouvé, None sinon
        """
        return ConfirmationAide.objects.filter(id=confirmation_aide_id).first()

    def create(self, **kwargs) -> ConfirmationAide:
        """
        Créer un nouveau confirmation_aide.

        Args:
            **kwargs: Données du confirmation_aide

        Returns:
            ConfirmationAide: Le confirmation_aide créé
        """
        return ConfirmationAide.objects.create(**kwargs)

    def update(self, confirmation_aide: ConfirmationAide, **kwargs) -> ConfirmationAide:
        """
        Mettre à jour un confirmation_aide existant.

        Args:
            confirmation_aide (ConfirmationAide): Le confirmation_aide à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            ConfirmationAide: Le confirmation_aide mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(confirmation_aide, field):
                setattr(confirmation_aide, field, value)

        confirmation_aide.save()
        return confirmation_aide

    def delete(self, confirmation_aide: ConfirmationAide) -> bool:
        """
        Supprimer un confirmation_aide.

        Args:
            confirmation_aide (ConfirmationAide): Le confirmation_aide à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        confirmation_aide.delete()
        return True

    def exists_by_id(self, confirmation_aide_id: int) -> bool:
        """
        Vérifier si un confirmation_aide existe par ID.

        Args:
            confirmation_aide_id (int): L'ID du confirmation_aide

        Returns:
            bool: True si le confirmation_aide existe, False sinon
        """
        return ConfirmationAide.objects.filter(id=confirmation_aide_id).exists()