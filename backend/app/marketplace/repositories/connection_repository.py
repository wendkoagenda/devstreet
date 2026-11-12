"""
Connection repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.marketplace.models import Connection
from app.marketplace.interfaces.connection_repository_interface import ConnectionRepositoryInterface


class ConnectionRepository(ConnectionRepositoryInterface):
    """
    Implémentation concrète des opérations du repository connections.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('status',)
    ORDERING_FIELDS = ('id', 'status', 'matched_at', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les connection, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les connection filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = Connection.objects.all()
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

    def get_by_id(self, connection_id: int) -> Optional[Connection]:
        """
        Obtenir un connection par ID.

        Args:
            connection_id (int): L'ID du connection

        Returns:
            Optional[Connection]: Le connection si trouvé, None sinon
        """
        return Connection.objects.filter(id=connection_id).first()

    def create(self, **kwargs) -> Connection:
        """
        Créer un nouveau connection.

        Args:
            **kwargs: Données du connection

        Returns:
            Connection: Le connection créé
        """
        return Connection.objects.create(**kwargs)

    def update(self, connection: Connection, **kwargs) -> Connection:
        """
        Mettre à jour un connection existant.

        Args:
            connection (Connection): Le connection à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Connection: Le connection mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(connection, field):
                setattr(connection, field, value)

        connection.save()
        return connection

    def delete(self, connection: Connection) -> bool:
        """
        Supprimer un connection.

        Args:
            connection (Connection): Le connection à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        connection.delete()
        return True

    def exists_by_id(self, connection_id: int) -> bool:
        """
        Vérifier si un connection existe par ID.

        Args:
            connection_id (int): L'ID du connection

        Returns:
            bool: True si le connection existe, False sinon
        """
        return Connection.objects.filter(id=connection_id).exists()