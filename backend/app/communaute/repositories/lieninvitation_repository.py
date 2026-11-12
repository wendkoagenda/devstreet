"""
LienInvitation repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.communaute.models import LienInvitation
from app.communaute.interfaces.lieninvitation_repository_interface import LienInvitationRepositoryInterface


class LienInvitationRepository(LienInvitationRepositoryInterface):
    """
    Implémentation concrète des opérations du repository lieninvitations.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('code_hash',)
    ORDERING_FIELDS = ('id', 'code_hash', 'previsualisation_autorisee', 'revoked_at', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les lien_invitation, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les lien_invitation filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = LienInvitation.objects.all()
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

    def get_by_id(self, lien_invitation_id: int) -> Optional[LienInvitation]:
        """
        Obtenir un lien_invitation par ID.

        Args:
            lien_invitation_id (int): L'ID du lien_invitation

        Returns:
            Optional[LienInvitation]: Le lien_invitation si trouvé, None sinon
        """
        return LienInvitation.objects.filter(id=lien_invitation_id).first()

    def create(self, **kwargs) -> LienInvitation:
        """
        Créer un nouveau lien_invitation.

        Args:
            **kwargs: Données du lien_invitation

        Returns:
            LienInvitation: Le lien_invitation créé
        """
        return LienInvitation.objects.create(**kwargs)

    def update(self, lien_invitation: LienInvitation, **kwargs) -> LienInvitation:
        """
        Mettre à jour un lien_invitation existant.

        Args:
            lien_invitation (LienInvitation): Le lien_invitation à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            LienInvitation: Le lien_invitation mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(lien_invitation, field):
                setattr(lien_invitation, field, value)

        lien_invitation.save()
        return lien_invitation

    def delete(self, lien_invitation: LienInvitation) -> bool:
        """
        Supprimer un lien_invitation.

        Args:
            lien_invitation (LienInvitation): Le lien_invitation à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        lien_invitation.delete()
        return True

    def exists_by_id(self, lien_invitation_id: int) -> bool:
        """
        Vérifier si un lien_invitation existe par ID.

        Args:
            lien_invitation_id (int): L'ID du lien_invitation

        Returns:
            bool: True si le lien_invitation existe, False sinon
        """
        return LienInvitation.objects.filter(id=lien_invitation_id).exists()