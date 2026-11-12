"""
Profil repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.marketplace.models import Profil
from app.marketplace.interfaces.profil_repository_interface import ProfilRepositoryInterface


class ProfilRepository(ProfilRepositoryInterface):
    """
    Implémentation concrète des opérations du repository profils.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('slug', 'headline', 'bio', 'phone', 'country', 'city', 'timezone', 'currency', 'github_url', 'linkedin_url', 'portfolio_url', 'cv_visibility',)
    ORDERING_FIELDS = ('id', 'is_company_owner', 'slug', 'photo', 'headline', 'bio', 'phone', 'country', 'city', 'remote', 'timezone', 'default_hours_per_week', 'is_open_to_work', 'daily_rate', 'currency', 'years_of_experience', 'github_url', 'linkedin_url', 'portfolio_url', 'cv_visibility', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les profil, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les profil filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = Profil.objects.all()
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

    def get_by_id(self, profil_id: int) -> Optional[Profil]:
        """
        Obtenir un profil par ID.

        Args:
            profil_id (int): L'ID du profil

        Returns:
            Optional[Profil]: Le profil si trouvé, None sinon
        """
        return Profil.objects.filter(id=profil_id).first()

    def create(self, **kwargs) -> Profil:
        """
        Créer un nouveau profil.

        Args:
            **kwargs: Données du profil

        Returns:
            Profil: Le profil créé
        """
        return Profil.objects.create(**kwargs)

    def update(self, profil: Profil, **kwargs) -> Profil:
        """
        Mettre à jour un profil existant.

        Args:
            profil (Profil): Le profil à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Profil: Le profil mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(profil, field):
                setattr(profil, field, value)

        profil.save()
        return profil

    def delete(self, profil: Profil) -> bool:
        """
        Supprimer un profil.

        Args:
            profil (Profil): Le profil à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        profil.delete()
        return True

    def exists_by_id(self, profil_id: int) -> bool:
        """
        Vérifier si un profil existe par ID.

        Args:
            profil_id (int): L'ID du profil

        Returns:
            bool: True si le profil existe, False sinon
        """
        return Profil.objects.filter(id=profil_id).exists()