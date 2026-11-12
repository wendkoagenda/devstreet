"""
Dragon repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.metier.models import Dragon
from app.metier.interfaces.dragon_repository_interface import DragonRepositoryInterface


class DragonRepository(DragonRepositoryInterface):
    """
    Implémentation concrète des opérations du repository dragons.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('titre', 'statut', 'description',)
    ORDERING_FIELDS = ('id', 'uuid', 'titre', 'statut', 'description', 'prix', 'document', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les dragon, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les dragon filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = Dragon.objects.all()
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

    def get_by_id(self, dragon_id: int) -> Optional[Dragon]:
        """
        Obtenir un dragon par ID.

        Args:
            dragon_id (int): L'ID du dragon

        Returns:
            Optional[Dragon]: Le dragon si trouvé, None sinon
        """
        return Dragon.objects.filter(id=dragon_id).first()

    def get_by_uuid(self, uuid: str) -> Optional[Dragon]:
        """
        Obtenir un dragon par UUID.

        Args:
            uuid (str): L'UUID du dragon

        Returns:
            Optional[Dragon]: Le dragon si trouvé, None sinon
        """
        return Dragon.objects.filter(uuid=uuid).first()

    def create(self, **kwargs) -> Dragon:
        """
        Créer un nouveau dragon.

        Args:
            **kwargs: Données du dragon

        Returns:
            Dragon: Le dragon créé
        """
        return Dragon.objects.create(**kwargs)

    def update(self, dragon: Dragon, **kwargs) -> Dragon:
        """
        Mettre à jour un dragon existant.

        Args:
            dragon (Dragon): Le dragon à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Dragon: Le dragon mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(dragon, field):
                setattr(dragon, field, value)

        dragon.save()
        return dragon

    def delete(self, dragon: Dragon) -> bool:
        """
        Supprimer un dragon.

        Args:
            dragon (Dragon): Le dragon à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        dragon.delete()
        return True

    def exists_by_id(self, dragon_id: int) -> bool:
        """
        Vérifier si un dragon existe par ID.

        Args:
            dragon_id (int): L'ID du dragon

        Returns:
            bool: True si le dragon existe, False sinon
        """
        return Dragon.objects.filter(id=dragon_id).exists()