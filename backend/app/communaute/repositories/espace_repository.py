"""
Espace repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.communaute.models import Espace
from app.communaute.interfaces.espace_repository_interface import EspaceRepositoryInterface


class EspaceRepository(EspaceRepositoryInterface):
    """
    Implémentation concrète des opérations du repository espaces.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('type', 'nom', 'description', 'acces',)
    ORDERING_FIELDS = ('id', 'type', 'nom', 'description', 'acces', 'membres_peuvent_publier', 'commentaires_ouverts', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les espace, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les espace filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = Espace.objects.all()
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

    def get_by_id(self, espace_id: int) -> Optional[Espace]:
        """
        Obtenir un espace par ID.

        Args:
            espace_id (int): L'ID du espace

        Returns:
            Optional[Espace]: Le espace si trouvé, None sinon
        """
        return Espace.objects.filter(id=espace_id).first()

    def create(self, **kwargs) -> Espace:
        """
        Créer un nouveau espace.

        Args:
            **kwargs: Données du espace

        Returns:
            Espace: Le espace créé
        """
        return Espace.objects.create(**kwargs)

    def update(self, espace: Espace, **kwargs) -> Espace:
        """
        Mettre à jour un espace existant.

        Args:
            espace (Espace): Le espace à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Espace: Le espace mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(espace, field):
                setattr(espace, field, value)

        espace.save()
        return espace

    def delete(self, espace: Espace) -> bool:
        """
        Supprimer un espace.

        Args:
            espace (Espace): Le espace à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        espace.delete()
        return True

    def exists_by_id(self, espace_id: int) -> bool:
        """
        Vérifier si un espace existe par ID.

        Args:
            espace_id (int): L'ID du espace

        Returns:
            bool: True si le espace existe, False sinon
        """
        return Espace.objects.filter(id=espace_id).exists()