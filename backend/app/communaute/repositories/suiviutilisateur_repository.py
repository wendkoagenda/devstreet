"""
SuiviUtilisateur repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.communaute.models import SuiviUtilisateur
from app.communaute.interfaces.suiviutilisateur_repository_interface import SuiviUtilisateurRepositoryInterface


class SuiviUtilisateurRepository(SuiviUtilisateurRepositoryInterface):
    """
    Implémentation concrète des opérations du repository suiviutilisateurs.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ()
    ORDERING_FIELDS = ('id', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les suivi_utilisateur, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les suivi_utilisateur filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = SuiviUtilisateur.objects.all()
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

    def get_by_id(self, suivi_utilisateur_id: int) -> Optional[SuiviUtilisateur]:
        """
        Obtenir un suivi_utilisateur par ID.

        Args:
            suivi_utilisateur_id (int): L'ID du suivi_utilisateur

        Returns:
            Optional[SuiviUtilisateur]: Le suivi_utilisateur si trouvé, None sinon
        """
        return SuiviUtilisateur.objects.filter(id=suivi_utilisateur_id).first()

    def create(self, **kwargs) -> SuiviUtilisateur:
        """
        Créer un nouveau suivi_utilisateur.

        Args:
            **kwargs: Données du suivi_utilisateur

        Returns:
            SuiviUtilisateur: Le suivi_utilisateur créé
        """
        return SuiviUtilisateur.objects.create(**kwargs)

    def update(self, suivi_utilisateur: SuiviUtilisateur, **kwargs) -> SuiviUtilisateur:
        """
        Mettre à jour un suivi_utilisateur existant.

        Args:
            suivi_utilisateur (SuiviUtilisateur): Le suivi_utilisateur à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            SuiviUtilisateur: Le suivi_utilisateur mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(suivi_utilisateur, field):
                setattr(suivi_utilisateur, field, value)

        suivi_utilisateur.save()
        return suivi_utilisateur

    def delete(self, suivi_utilisateur: SuiviUtilisateur) -> bool:
        """
        Supprimer un suivi_utilisateur.

        Args:
            suivi_utilisateur (SuiviUtilisateur): Le suivi_utilisateur à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        suivi_utilisateur.delete()
        return True

    def exists_by_id(self, suivi_utilisateur_id: int) -> bool:
        """
        Vérifier si un suivi_utilisateur existe par ID.

        Args:
            suivi_utilisateur_id (int): L'ID du suivi_utilisateur

        Returns:
            bool: True si le suivi_utilisateur existe, False sinon
        """
        return SuiviUtilisateur.objects.filter(id=suivi_utilisateur_id).exists()