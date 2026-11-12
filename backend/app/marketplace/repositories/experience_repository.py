"""
Experience repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.marketplace.models import Experience
from app.marketplace.interfaces.experience_repository_interface import ExperienceRepositoryInterface


class ExperienceRepository(ExperienceRepositoryInterface):
    """
    Implémentation concrète des opérations du repository experiences.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('title', 'company_name', 'location', 'contract_type', 'description', 'technologies',)
    ORDERING_FIELDS = ('id', 'title', 'company_name', 'location', 'contract_type', 'start_date', 'end_date', 'is_current', 'description', 'technologies', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les experience, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les experience filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = Experience.objects.all()
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

    def get_by_id(self, experience_id: int) -> Optional[Experience]:
        """
        Obtenir un experience par ID.

        Args:
            experience_id (int): L'ID du experience

        Returns:
            Optional[Experience]: Le experience si trouvé, None sinon
        """
        return Experience.objects.filter(id=experience_id).first()

    def create(self, **kwargs) -> Experience:
        """
        Créer un nouveau experience.

        Args:
            **kwargs: Données du experience

        Returns:
            Experience: Le experience créé
        """
        return Experience.objects.create(**kwargs)

    def update(self, experience: Experience, **kwargs) -> Experience:
        """
        Mettre à jour un experience existant.

        Args:
            experience (Experience): Le experience à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Experience: Le experience mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(experience, field):
                setattr(experience, field, value)

        experience.save()
        return experience

    def delete(self, experience: Experience) -> bool:
        """
        Supprimer un experience.

        Args:
            experience (Experience): Le experience à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        experience.delete()
        return True

    def exists_by_id(self, experience_id: int) -> bool:
        """
        Vérifier si un experience existe par ID.

        Args:
            experience_id (int): L'ID du experience

        Returns:
            bool: True si le experience existe, False sinon
        """
        return Experience.objects.filter(id=experience_id).exists()