"""
Skill repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.marketplace.models import Skill
from app.marketplace.interfaces.skill_repository_interface import SkillRepositoryInterface


class SkillRepository(SkillRepositoryInterface):
    """
    Implémentation concrète des opérations du repository skills.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('name', 'slug', 'type', 'category',)
    ORDERING_FIELDS = ('id', 'name', 'slug', 'type', 'category', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les skill, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les skill filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = Skill.objects.all()
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

    def get_by_id(self, skill_id: int) -> Optional[Skill]:
        """
        Obtenir un skill par ID.

        Args:
            skill_id (int): L'ID du skill

        Returns:
            Optional[Skill]: Le skill si trouvé, None sinon
        """
        return Skill.objects.filter(id=skill_id).first()

    def create(self, **kwargs) -> Skill:
        """
        Créer un nouveau skill.

        Args:
            **kwargs: Données du skill

        Returns:
            Skill: Le skill créé
        """
        return Skill.objects.create(**kwargs)

    def update(self, skill: Skill, **kwargs) -> Skill:
        """
        Mettre à jour un skill existant.

        Args:
            skill (Skill): Le skill à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Skill: Le skill mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(skill, field):
                setattr(skill, field, value)

        skill.save()
        return skill

    def delete(self, skill: Skill) -> bool:
        """
        Supprimer un skill.

        Args:
            skill (Skill): Le skill à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        skill.delete()
        return True

    def exists_by_id(self, skill_id: int) -> bool:
        """
        Vérifier si un skill existe par ID.

        Args:
            skill_id (int): L'ID du skill

        Returns:
            bool: True si le skill existe, False sinon
        """
        return Skill.objects.filter(id=skill_id).exists()