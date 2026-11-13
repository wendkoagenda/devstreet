"""
ImagePublication repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.communaute.models import ImagePublication
from app.communaute.interfaces.imagepublication_repository_interface import ImagePublicationRepositoryInterface


class ImagePublicationRepository(ImagePublicationRepositoryInterface):
    """
    Implémentation concrète des opérations du repository imagepublications.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('url', 'texte_alternatif',)
    ORDERING_FIELDS = ('id', 'url', 'texte_alternatif', 'position', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les image_publication, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les image_publication filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = ImagePublication.objects.all()
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

    def get_by_id(self, image_publication_id: int) -> Optional[ImagePublication]:
        """
        Obtenir un image_publication par ID.

        Args:
            image_publication_id (int): L'ID du image_publication

        Returns:
            Optional[ImagePublication]: Le image_publication si trouvé, None sinon
        """
        return ImagePublication.objects.filter(id=image_publication_id).first()

    def create(self, **kwargs) -> ImagePublication:
        """
        Créer un nouveau image_publication.

        Args:
            **kwargs: Données du image_publication

        Returns:
            ImagePublication: Le image_publication créé
        """
        return ImagePublication.objects.create(**kwargs)

    def update(self, image_publication: ImagePublication, **kwargs) -> ImagePublication:
        """
        Mettre à jour un image_publication existant.

        Args:
            image_publication (ImagePublication): Le image_publication à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            ImagePublication: Le image_publication mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(image_publication, field):
                setattr(image_publication, field, value)

        image_publication.save()
        return image_publication

    def delete(self, image_publication: ImagePublication) -> bool:
        """
        Supprimer un image_publication.

        Args:
            image_publication (ImagePublication): Le image_publication à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        image_publication.delete()
        return True

    def exists_by_id(self, image_publication_id: int) -> bool:
        """
        Vérifier si un image_publication existe par ID.

        Args:
            image_publication_id (int): L'ID du image_publication

        Returns:
            bool: True si le image_publication existe, False sinon
        """
        return ImagePublication.objects.filter(id=image_publication_id).exists()