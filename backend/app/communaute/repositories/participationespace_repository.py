"""
ParticipationEspace repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.communaute.models import ParticipationEspace
from app.communaute.interfaces.participationespace_repository_interface import ParticipationEspaceRepositoryInterface


class ParticipationEspaceRepository(ParticipationEspaceRepositoryInterface):
    """
    Implémentation concrète des opérations du repository participationespaces.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('role',)
    ORDERING_FIELDS = ('id', 'role', 'joined_at', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les participation_espace, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les participation_espace filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = ParticipationEspace.objects.all()
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

    def get_by_id(self, participation_espace_id: int) -> Optional[ParticipationEspace]:
        """
        Obtenir un participation_espace par ID.

        Args:
            participation_espace_id (int): L'ID du participation_espace

        Returns:
            Optional[ParticipationEspace]: Le participation_espace si trouvé, None sinon
        """
        return ParticipationEspace.objects.filter(id=participation_espace_id).first()

    def create(self, **kwargs) -> ParticipationEspace:
        """
        Créer un nouveau participation_espace.

        Args:
            **kwargs: Données du participation_espace

        Returns:
            ParticipationEspace: Le participation_espace créé
        """
        return ParticipationEspace.objects.create(**kwargs)

    def update(self, participation_espace: ParticipationEspace, **kwargs) -> ParticipationEspace:
        """
        Mettre à jour un participation_espace existant.

        Args:
            participation_espace (ParticipationEspace): Le participation_espace à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            ParticipationEspace: Le participation_espace mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(participation_espace, field):
                setattr(participation_espace, field, value)

        participation_espace.save()
        return participation_espace

    def delete(self, participation_espace: ParticipationEspace) -> bool:
        """
        Supprimer un participation_espace.

        Args:
            participation_espace (ParticipationEspace): Le participation_espace à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        participation_espace.delete()
        return True

    def exists_by_id(self, participation_espace_id: int) -> bool:
        """
        Vérifier si un participation_espace existe par ID.

        Args:
            participation_espace_id (int): L'ID du participation_espace

        Returns:
            bool: True si le participation_espace existe, False sinon
        """
        return ParticipationEspace.objects.filter(id=participation_espace_id).exists()