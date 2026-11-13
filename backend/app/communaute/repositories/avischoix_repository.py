"""
AvisChoix repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.communaute.models import AvisChoix
from app.communaute.interfaces.avischoix_repository_interface import AvisChoixRepositoryInterface


class AvisChoixRepository(AvisChoixRepositoryInterface):
    """
    Implémentation concrète des opérations du repository avischoixs.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('explication',)
    ORDERING_FIELDS = ('id', 'explication', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les avis_choix, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les avis_choix filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = AvisChoix.objects.all()
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

    def get_by_id(self, avis_choix_id: int) -> Optional[AvisChoix]:
        """
        Obtenir un avis_choix par ID.

        Args:
            avis_choix_id (int): L'ID du avis_choix

        Returns:
            Optional[AvisChoix]: Le avis_choix si trouvé, None sinon
        """
        return AvisChoix.objects.filter(id=avis_choix_id).first()

    def create(self, **kwargs) -> AvisChoix:
        """
        Créer un nouveau avis_choix.

        Args:
            **kwargs: Données du avis_choix

        Returns:
            AvisChoix: Le avis_choix créé
        """
        return AvisChoix.objects.create(**kwargs)

    def update(self, avis_choix: AvisChoix, **kwargs) -> AvisChoix:
        """
        Mettre à jour un avis_choix existant.

        Args:
            avis_choix (AvisChoix): Le avis_choix à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            AvisChoix: Le avis_choix mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(avis_choix, field):
                setattr(avis_choix, field, value)

        avis_choix.save()
        return avis_choix

    def delete(self, avis_choix: AvisChoix) -> bool:
        """
        Supprimer un avis_choix.

        Args:
            avis_choix (AvisChoix): Le avis_choix à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        avis_choix.delete()
        return True

    def exists_by_id(self, avis_choix_id: int) -> bool:
        """
        Vérifier si un avis_choix existe par ID.

        Args:
            avis_choix_id (int): L'ID du avis_choix

        Returns:
            bool: True si le avis_choix existe, False sinon
        """
        return AvisChoix.objects.filter(id=avis_choix_id).exists()