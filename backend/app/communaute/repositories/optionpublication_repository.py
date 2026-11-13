"""
OptionPublication repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.communaute.models import OptionPublication
from app.communaute.interfaces.optionpublication_repository_interface import OptionPublicationRepositoryInterface


class OptionPublicationRepository(OptionPublicationRepositoryInterface):
    """
    Implémentation concrète des opérations du repository optionpublications.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('libelle', 'description', 'image_url',)
    ORDERING_FIELDS = ('id', 'libelle', 'description', 'image_url', 'position', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les option_publication, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les option_publication filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = OptionPublication.objects.all()
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

    def get_by_id(self, option_publication_id: int) -> Optional[OptionPublication]:
        """
        Obtenir un option_publication par ID.

        Args:
            option_publication_id (int): L'ID du option_publication

        Returns:
            Optional[OptionPublication]: Le option_publication si trouvé, None sinon
        """
        return OptionPublication.objects.filter(id=option_publication_id).first()

    def create(self, **kwargs) -> OptionPublication:
        """
        Créer un nouveau option_publication.

        Args:
            **kwargs: Données du option_publication

        Returns:
            OptionPublication: Le option_publication créé
        """
        return OptionPublication.objects.create(**kwargs)

    def update(self, option_publication: OptionPublication, **kwargs) -> OptionPublication:
        """
        Mettre à jour un option_publication existant.

        Args:
            option_publication (OptionPublication): Le option_publication à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            OptionPublication: Le option_publication mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(option_publication, field):
                setattr(option_publication, field, value)

        option_publication.save()
        return option_publication

    def delete(self, option_publication: OptionPublication) -> bool:
        """
        Supprimer un option_publication.

        Args:
            option_publication (OptionPublication): Le option_publication à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        option_publication.delete()
        return True

    def exists_by_id(self, option_publication_id: int) -> bool:
        """
        Vérifier si un option_publication existe par ID.

        Args:
            option_publication_id (int): L'ID du option_publication

        Returns:
            bool: True si le option_publication existe, False sinon
        """
        return OptionPublication.objects.filter(id=option_publication_id).exists()