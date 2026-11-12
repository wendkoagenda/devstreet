"""
Gado repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.garoapp.models import Gado
from app.garoapp.interfaces.gado_repository_interface import GadoRepositoryInterface


class GadoRepository(GadoRepositoryInterface):
    """
    Implémentation concrète des opérations du repository gados.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('titre', 'statut', 'description',)
    ORDERING_FIELDS = ('id', 'uuid', 'titre', 'statut', 'description', 'prix', 'document', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les gado, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les gado filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = Gado.objects.all()
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

    def get_by_id(self, gado_id: int) -> Optional[Gado]:
        """
        Obtenir un gado par ID.

        Args:
            gado_id (int): L'ID du gado

        Returns:
            Optional[Gado]: Le gado si trouvé, None sinon
        """
        return Gado.objects.filter(id=gado_id).first()

    def get_by_uuid(self, uuid: str) -> Optional[Gado]:
        """
        Obtenir un gado par UUID.

        Args:
            uuid (str): L'UUID du gado

        Returns:
            Optional[Gado]: Le gado si trouvé, None sinon
        """
        return Gado.objects.filter(uuid=uuid).first()

    def create(self, **kwargs) -> Gado:
        """
        Créer un nouveau gado.

        Args:
            **kwargs: Données du gado

        Returns:
            Gado: Le gado créé
        """
        return Gado.objects.create(**kwargs)

    def update(self, gado: Gado, **kwargs) -> Gado:
        """
        Mettre à jour un gado existant.

        Args:
            gado (Gado): Le gado à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Gado: Le gado mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(gado, field):
                setattr(gado, field, value)

        gado.save()
        return gado

    def delete(self, gado: Gado) -> bool:
        """
        Supprimer un gado.

        Args:
            gado (Gado): Le gado à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        gado.delete()
        return True

    def exists_by_id(self, gado_id: int) -> bool:
        """
        Vérifier si un gado existe par ID.

        Args:
            gado_id (int): L'ID du gado

        Returns:
            bool: True si le gado existe, False sinon
        """
        return Gado.objects.filter(id=gado_id).exists()