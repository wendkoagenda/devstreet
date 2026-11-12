"""
Elitest repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.metier.models import Elitest
from app.metier.interfaces.elitest_repository_interface import ElitestRepositoryInterface


class ElitestRepository(ElitestRepositoryInterface):
    """
    Implémentation concrète des opérations du repository elitests.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('titre', 'statut', 'description')
    ORDERING_FIELDS = ('id', 'uuid', 'titre', 'statut', 'description', 'prix', 'document', 'created_at', 'updated_at')

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les elitests, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les elitests filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = Elitest.objects.all()
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

    def get_by_id(self, metier_id: int) -> Optional[Elitest]:
        """
        Obtenir un metier par ID.

        Args:
            metier_id (int): L'ID du metier

        Returns:
            Optional[Elitest]: Le metier si trouvé, None sinon
        """
        return Elitest.objects.filter(id=metier_id).first()

    def get_by_uuid(self, uuid: str) -> Optional[Elitest]:
        """
        Obtenir un metier par UUID.

        Args:
            uuid (str): L'UUID du metier

        Returns:
            Optional[Elitest]: Le metier si trouvé, None sinon
        """
        return Elitest.objects.filter(uuid=uuid).first()

    def create(self, **kwargs) -> Elitest:
        """
        Créer un nouveau metier.

        Args:
            **kwargs: Données du metier

        Returns:
            Elitest: Le metier créé
        """
        return Elitest.objects.create(**kwargs)

    def update(self, metier: Elitest, **kwargs) -> Elitest:
        """
        Mettre à jour un metier existant.

        Args:
            metier (Elitest): Le metier à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Elitest: Le metier mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(metier, field):
                setattr(metier, field, value)

        metier.save()
        return metier

    def delete(self, metier: Elitest) -> bool:
        """
        Supprimer un metier.

        Args:
            metier (Elitest): Le metier à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        metier.delete()
        return True

    def exists_by_id(self, metier_id: int) -> bool:
        """
        Vérifier si un metier existe par ID.

        Args:
            metier_id (int): L'ID du metier

        Returns:
            bool: True si le metier existe, False sinon
        """
        return Elitest.objects.filter(id=metier_id).exists()