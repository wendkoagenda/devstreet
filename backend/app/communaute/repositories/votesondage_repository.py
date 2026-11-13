"""
VoteSondage repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.communaute.models import VoteSondage
from app.communaute.interfaces.votesondage_repository_interface import VoteSondageRepositoryInterface


class VoteSondageRepository(VoteSondageRepositoryInterface):
    """
    Implémentation concrète des opérations du repository votesondages.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ()
    ORDERING_FIELDS = ('id', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les vote_sondage, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les vote_sondage filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = VoteSondage.objects.all()
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

    def get_by_id(self, vote_sondage_id: int) -> Optional[VoteSondage]:
        """
        Obtenir un vote_sondage par ID.

        Args:
            vote_sondage_id (int): L'ID du vote_sondage

        Returns:
            Optional[VoteSondage]: Le vote_sondage si trouvé, None sinon
        """
        return VoteSondage.objects.filter(id=vote_sondage_id).first()

    def create(self, **kwargs) -> VoteSondage:
        """
        Créer un nouveau vote_sondage.

        Args:
            **kwargs: Données du vote_sondage

        Returns:
            VoteSondage: Le vote_sondage créé
        """
        return VoteSondage.objects.create(**kwargs)

    def update(self, vote_sondage: VoteSondage, **kwargs) -> VoteSondage:
        """
        Mettre à jour un vote_sondage existant.

        Args:
            vote_sondage (VoteSondage): Le vote_sondage à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            VoteSondage: Le vote_sondage mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(vote_sondage, field):
                setattr(vote_sondage, field, value)

        vote_sondage.save()
        return vote_sondage

    def delete(self, vote_sondage: VoteSondage) -> bool:
        """
        Supprimer un vote_sondage.

        Args:
            vote_sondage (VoteSondage): Le vote_sondage à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        vote_sondage.delete()
        return True

    def exists_by_id(self, vote_sondage_id: int) -> bool:
        """
        Vérifier si un vote_sondage existe par ID.

        Args:
            vote_sondage_id (int): L'ID du vote_sondage

        Returns:
            bool: True si le vote_sondage existe, False sinon
        """
        return VoteSondage.objects.filter(id=vote_sondage_id).exists()