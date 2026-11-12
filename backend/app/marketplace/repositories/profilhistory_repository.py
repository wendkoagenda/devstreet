"""
ProfilHistory repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.marketplace.models import ProfilHistory
from app.marketplace.interfaces.profilhistory_repository_interface import ProfilHistoryRepositoryInterface


class ProfilHistoryRepository(ProfilHistoryRepositoryInterface):
    """
    Implémentation concrète des opérations du repository profilhistorys.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('field', 'old_value', 'new_value', 'source',)
    ORDERING_FIELDS = ('id', 'field', 'old_value', 'new_value', 'source', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les profil_history, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les profil_history filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = ProfilHistory.objects.all()
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

    def get_by_id(self, profil_history_id: int) -> Optional[ProfilHistory]:
        """
        Obtenir un profil_history par ID.

        Args:
            profil_history_id (int): L'ID du profil_history

        Returns:
            Optional[ProfilHistory]: Le profil_history si trouvé, None sinon
        """
        return ProfilHistory.objects.filter(id=profil_history_id).first()

    def create(self, **kwargs) -> ProfilHistory:
        """
        Créer un nouveau profil_history.

        Args:
            **kwargs: Données du profil_history

        Returns:
            ProfilHistory: Le profil_history créé
        """
        return ProfilHistory.objects.create(**kwargs)

    def update(self, profil_history: ProfilHistory, **kwargs) -> ProfilHistory:
        """
        Mettre à jour un profil_history existant.

        Args:
            profil_history (ProfilHistory): Le profil_history à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            ProfilHistory: Le profil_history mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(profil_history, field):
                setattr(profil_history, field, value)

        profil_history.save()
        return profil_history

    def delete(self, profil_history: ProfilHistory) -> bool:
        """
        Supprimer un profil_history.

        Args:
            profil_history (ProfilHistory): Le profil_history à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        profil_history.delete()
        return True

    def exists_by_id(self, profil_history_id: int) -> bool:
        """
        Vérifier si un profil_history existe par ID.

        Args:
            profil_history_id (int): L'ID du profil_history

        Returns:
            bool: True si le profil_history existe, False sinon
        """
        return ProfilHistory.objects.filter(id=profil_history_id).exists()