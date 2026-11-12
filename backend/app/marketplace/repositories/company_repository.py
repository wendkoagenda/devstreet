"""
Company repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.marketplace.models import Company
from app.marketplace.interfaces.company_repository_interface import CompanyRepositoryInterface


class CompanyRepository(CompanyRepositoryInterface):
    """
    Implémentation concrète des opérations du repository companys.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('name', 'slug', 'description', 'sector', 'size', 'website', 'contact_email', 'phone', 'country', 'city', 'address',)
    ORDERING_FIELDS = ('id', 'name', 'slug', 'logo', 'description', 'sector', 'size', 'website', 'contact_email', 'phone', 'country', 'city', 'address', 'is_verified', 'verified_at', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les company, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les company filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = Company.objects.all()
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

    def get_by_id(self, company_id: int) -> Optional[Company]:
        """
        Obtenir un company par ID.

        Args:
            company_id (int): L'ID du company

        Returns:
            Optional[Company]: Le company si trouvé, None sinon
        """
        return Company.objects.filter(id=company_id).first()

    def create(self, **kwargs) -> Company:
        """
        Créer un nouveau company.

        Args:
            **kwargs: Données du company

        Returns:
            Company: Le company créé
        """
        return Company.objects.create(**kwargs)

    def update(self, company: Company, **kwargs) -> Company:
        """
        Mettre à jour un company existant.

        Args:
            company (Company): Le company à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Company: Le company mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(company, field):
                setattr(company, field, value)

        company.save()
        return company

    def delete(self, company: Company) -> bool:
        """
        Supprimer un company.

        Args:
            company (Company): Le company à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        company.delete()
        return True

    def exists_by_id(self, company_id: int) -> bool:
        """
        Vérifier si un company existe par ID.

        Args:
            company_id (int): L'ID du company

        Returns:
            bool: True si le company existe, False sinon
        """
        return Company.objects.filter(id=company_id).exists()