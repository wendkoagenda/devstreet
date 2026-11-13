"""
LikePublication repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.communaute.models import LikePublication
from app.communaute.interfaces.likepublication_repository_interface import LikePublicationRepositoryInterface


class LikePublicationRepository(LikePublicationRepositoryInterface):
    """
    Implémentation concrète des opérations du repository likepublications.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ()
    ORDERING_FIELDS = ('id', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les like_publication, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les like_publication filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = LikePublication.objects.all()
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

    def get_by_id(self, like_publication_id: int) -> Optional[LikePublication]:
        """
        Obtenir un like_publication par ID.

        Args:
            like_publication_id (int): L'ID du like_publication

        Returns:
            Optional[LikePublication]: Le like_publication si trouvé, None sinon
        """
        return LikePublication.objects.filter(id=like_publication_id).first()

    def create(self, **kwargs) -> LikePublication:
        """
        Créer un nouveau like_publication.

        Args:
            **kwargs: Données du like_publication

        Returns:
            LikePublication: Le like_publication créé
        """
        return LikePublication.objects.create(**kwargs)

    def update(self, like_publication: LikePublication, **kwargs) -> LikePublication:
        """
        Mettre à jour un like_publication existant.

        Args:
            like_publication (LikePublication): Le like_publication à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            LikePublication: Le like_publication mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(like_publication, field):
                setattr(like_publication, field, value)

        like_publication.save()
        return like_publication

    def delete(self, like_publication: LikePublication) -> bool:
        """
        Supprimer un like_publication.

        Args:
            like_publication (LikePublication): Le like_publication à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        like_publication.delete()
        return True

    def exists_by_id(self, like_publication_id: int) -> bool:
        """
        Vérifier si un like_publication existe par ID.

        Args:
            like_publication_id (int): L'ID du like_publication

        Returns:
            bool: True si le like_publication existe, False sinon
        """
        return LikePublication.objects.filter(id=like_publication_id).exists()