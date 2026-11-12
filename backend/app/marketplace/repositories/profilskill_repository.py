"""
ProfilSkill repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.marketplace.models import ProfilSkill
from app.marketplace.interfaces.profilskill_repository_interface import ProfilSkillRepositoryInterface


class ProfilSkillRepository(ProfilSkillRepositoryInterface):
    """
    Implémentation concrète des opérations du repository profilskills.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ()
    ORDERING_FIELDS = ('id', 'level', 'years', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les profil_skill, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les profil_skill filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = ProfilSkill.objects.all()
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

    def get_by_id(self, profil_skill_id: int) -> Optional[ProfilSkill]:
        """
        Obtenir un profil_skill par ID.

        Args:
            profil_skill_id (int): L'ID du profil_skill

        Returns:
            Optional[ProfilSkill]: Le profil_skill si trouvé, None sinon
        """
        return ProfilSkill.objects.filter(id=profil_skill_id).first()

    def create(self, **kwargs) -> ProfilSkill:
        """
        Créer un nouveau profil_skill.

        Args:
            **kwargs: Données du profil_skill

        Returns:
            ProfilSkill: Le profil_skill créé
        """
        return ProfilSkill.objects.create(**kwargs)

    def update(self, profil_skill: ProfilSkill, **kwargs) -> ProfilSkill:
        """
        Mettre à jour un profil_skill existant.

        Args:
            profil_skill (ProfilSkill): Le profil_skill à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            ProfilSkill: Le profil_skill mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(profil_skill, field):
                setattr(profil_skill, field, value)

        profil_skill.save()
        return profil_skill

    def delete(self, profil_skill: ProfilSkill) -> bool:
        """
        Supprimer un profil_skill.

        Args:
            profil_skill (ProfilSkill): Le profil_skill à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        profil_skill.delete()
        return True

    def exists_by_id(self, profil_skill_id: int) -> bool:
        """
        Vérifier si un profil_skill existe par ID.

        Args:
            profil_skill_id (int): L'ID du profil_skill

        Returns:
            bool: True si le profil_skill existe, False sinon
        """
        return ProfilSkill.objects.filter(id=profil_skill_id).exists()