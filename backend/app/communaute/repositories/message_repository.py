"""
Message repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.communaute.models import Message
from app.communaute.interfaces.message_repository_interface import MessageRepositoryInterface


class MessageRepository(MessageRepositoryInterface):
    """
    Implémentation concrète des opérations du repository messages.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('texte',)
    ORDERING_FIELDS = ('id', 'texte', 'sent_at', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les message, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les message filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = Message.objects.all()
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

    def get_by_id(self, message_id: int) -> Optional[Message]:
        """
        Obtenir un message par ID.

        Args:
            message_id (int): L'ID du message

        Returns:
            Optional[Message]: Le message si trouvé, None sinon
        """
        return Message.objects.filter(id=message_id).first()

    def create(self, **kwargs) -> Message:
        """
        Créer un nouveau message.

        Args:
            **kwargs: Données du message

        Returns:
            Message: Le message créé
        """
        return Message.objects.create(**kwargs)

    def update(self, message: Message, **kwargs) -> Message:
        """
        Mettre à jour un message existant.

        Args:
            message (Message): Le message à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Message: Le message mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(message, field):
                setattr(message, field, value)

        message.save()
        return message

    def delete(self, message: Message) -> bool:
        """
        Supprimer un message.

        Args:
            message (Message): Le message à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        message.delete()
        return True

    def exists_by_id(self, message_id: int) -> bool:
        """
        Vérifier si un message existe par ID.

        Args:
            message_id (int): L'ID du message

        Returns:
            bool: True si le message existe, False sinon
        """
        return Message.objects.filter(id=message_id).exists()