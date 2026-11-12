"""
Elitesty repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.metier.models import Elitesty
from app.metier.interfaces.elitesty_repository_interface import ElitestyRepositoryInterface


class ElitestyRepository(ElitestyRepositoryInterface):
    """
    Implémentation concrète des opérations du repository elitestys.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('titre', 'statut', 'description',)
    ORDERING_FIELDS = ('id', 'uuid', 'titre', 'statut', 'description', 'prix', 'document', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les elitesty, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les elitesty filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = Elitesty.objects.all()
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

    def get_by_id(self, elitesty_id: int) -> Optional[Elitesty]:
        """
        Obtenir un elitesty par ID.

        Args:
            elitesty_id (int): L'ID du elitesty

        Returns:
            Optional[Elitesty]: Le elitesty si trouvé, None sinon
        """
        return Elitesty.objects.filter(id=elitesty_id).first()

    def get_by_uuid(self, uuid: str) -> Optional[Elitesty]:
        """
        Obtenir un elitesty par UUID.

        Args:
            uuid (str): L'UUID du elitesty

        Returns:
            Optional[Elitesty]: Le elitesty si trouvé, None sinon
        """
        return Elitesty.objects.filter(uuid=uuid).first()

    def create(self, **kwargs) -> Elitesty:
        """
        Créer un nouveau elitesty.

        Args:
            **kwargs: Données du elitesty

        Returns:
            Elitesty: Le elitesty créé
        """
        return Elitesty.objects.create(**kwargs)

    def update(self, elitesty: Elitesty, **kwargs) -> Elitesty:
        """
        Mettre à jour un elitesty existant.

        Args:
            elitesty (Elitesty): Le elitesty à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Elitesty: Le elitesty mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(elitesty, field):
                setattr(elitesty, field, value)

        elitesty.save()
        return elitesty

    def delete(self, elitesty: Elitesty) -> bool:
        """
        Supprimer un elitesty.

        Args:
            elitesty (Elitesty): Le elitesty à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        elitesty.delete()
        return True

    def exists_by_id(self, elitesty_id: int) -> bool:
        """
        Vérifier si un elitesty existe par ID.

        Args:
            elitesty_id (int): L'ID du elitesty

        Returns:
            bool: True si le elitesty existe, False sinon
        """
        return Elitesty.objects.filter(id=elitesty_id).exists()