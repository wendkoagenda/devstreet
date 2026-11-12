"""
Fusion repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.metier.models import Fusion
from app.metier.interfaces.fusion_repository_interface import FusionRepositoryInterface


class FusionRepository(FusionRepositoryInterface):
    """
    Implémentation concrète des opérations du repository fusions.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('titre', 'statut', 'description',)
    ORDERING_FIELDS = ('id', 'uuid', 'titre', 'statut', 'description', 'prix', 'document', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les fusion, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les fusion filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = Fusion.objects.all()
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

    def get_by_id(self, fusion_id: int) -> Optional[Fusion]:
        """
        Obtenir un fusion par ID.

        Args:
            fusion_id (int): L'ID du fusion

        Returns:
            Optional[Fusion]: Le fusion si trouvé, None sinon
        """
        return Fusion.objects.filter(id=fusion_id).first()

    def get_by_uuid(self, uuid: str) -> Optional[Fusion]:
        """
        Obtenir un fusion par UUID.

        Args:
            uuid (str): L'UUID du fusion

        Returns:
            Optional[Fusion]: Le fusion si trouvé, None sinon
        """
        return Fusion.objects.filter(uuid=uuid).first()

    def create(self, **kwargs) -> Fusion:
        """
        Créer un nouveau fusion.

        Args:
            **kwargs: Données du fusion

        Returns:
            Fusion: Le fusion créé
        """
        return Fusion.objects.create(**kwargs)

    def update(self, fusion: Fusion, **kwargs) -> Fusion:
        """
        Mettre à jour un fusion existant.

        Args:
            fusion (Fusion): Le fusion à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Fusion: Le fusion mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(fusion, field):
                setattr(fusion, field, value)

        fusion.save()
        return fusion

    def delete(self, fusion: Fusion) -> bool:
        """
        Supprimer un fusion.

        Args:
            fusion (Fusion): Le fusion à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        fusion.delete()
        return True

    def exists_by_id(self, fusion_id: int) -> bool:
        """
        Vérifier si un fusion existe par ID.

        Args:
            fusion_id (int): L'ID du fusion

        Returns:
            bool: True si le fusion existe, False sinon
        """
        return Fusion.objects.filter(id=fusion_id).exists()