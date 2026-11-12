"""
Conversation repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.communaute.models import Conversation
from app.communaute.interfaces.conversation_repository_interface import ConversationRepositoryInterface


class ConversationRepository(ConversationRepositoryInterface):
    """
    Implémentation concrète des opérations du repository conversations.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ()
    ORDERING_FIELDS = ('id', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les conversation, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les conversation filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = Conversation.objects.all()
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

    def get_by_id(self, conversation_id: int) -> Optional[Conversation]:
        """
        Obtenir un conversation par ID.

        Args:
            conversation_id (int): L'ID du conversation

        Returns:
            Optional[Conversation]: Le conversation si trouvé, None sinon
        """
        return Conversation.objects.filter(id=conversation_id).first()

    def create(self, **kwargs) -> Conversation:
        """
        Créer un nouveau conversation.

        Args:
            **kwargs: Données du conversation

        Returns:
            Conversation: Le conversation créé
        """
        return Conversation.objects.create(**kwargs)

    def update(self, conversation: Conversation, **kwargs) -> Conversation:
        """
        Mettre à jour un conversation existant.

        Args:
            conversation (Conversation): Le conversation à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Conversation: Le conversation mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(conversation, field):
                setattr(conversation, field, value)

        conversation.save()
        return conversation

    def delete(self, conversation: Conversation) -> bool:
        """
        Supprimer un conversation.

        Args:
            conversation (Conversation): Le conversation à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        conversation.delete()
        return True

    def exists_by_id(self, conversation_id: int) -> bool:
        """
        Vérifier si un conversation existe par ID.

        Args:
            conversation_id (int): L'ID du conversation

        Returns:
            bool: True si le conversation existe, False sinon
        """
        return Conversation.objects.filter(id=conversation_id).exists()