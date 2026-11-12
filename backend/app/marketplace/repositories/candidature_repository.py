"""
Candidature repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.marketplace.models import Candidature
from app.marketplace.interfaces.candidature_repository_interface import CandidatureRepositoryInterface


class CandidatureRepository(CandidatureRepositoryInterface):
    """
    Implémentation concrète des opérations du repository candidatures.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('message', 'status',)
    ORDERING_FIELDS = ('id', 'message', 'status', 'ai_match_score', 'cv_snapshot', 'decided_at', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les candidature, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les candidature filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = Candidature.objects.all()
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

    def get_by_id(self, candidature_id: int) -> Optional[Candidature]:
        """
        Obtenir un candidature par ID.

        Args:
            candidature_id (int): L'ID du candidature

        Returns:
            Optional[Candidature]: Le candidature si trouvé, None sinon
        """
        return Candidature.objects.filter(id=candidature_id).first()

    def create(self, **kwargs) -> Candidature:
        """
        Créer un nouveau candidature.

        Args:
            **kwargs: Données du candidature

        Returns:
            Candidature: Le candidature créé
        """
        return Candidature.objects.create(**kwargs)

    def update(self, candidature: Candidature, **kwargs) -> Candidature:
        """
        Mettre à jour un candidature existant.

        Args:
            candidature (Candidature): Le candidature à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Candidature: Le candidature mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(candidature, field):
                setattr(candidature, field, value)

        candidature.save()
        return candidature

    def delete(self, candidature: Candidature) -> bool:
        """
        Supprimer un candidature.

        Args:
            candidature (Candidature): Le candidature à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        candidature.delete()
        return True

    def exists_by_id(self, candidature_id: int) -> bool:
        """
        Vérifier si un candidature existe par ID.

        Args:
            candidature_id (int): L'ID du candidature

        Returns:
            bool: True si le candidature existe, False sinon
        """
        return Candidature.objects.filter(id=candidature_id).exists()