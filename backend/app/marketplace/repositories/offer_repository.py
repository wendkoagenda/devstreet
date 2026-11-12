"""
Offer repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.marketplace.models import Offer
from app.marketplace.interfaces.offer_repository_interface import OfferRepositoryInterface


class OfferRepository(OfferRepositoryInterface):
    """
    Implémentation concrète des opérations du repository offers.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('title', 'slug', 'description', 'type', 'experience_level', 'currency', 'budget_period', 'country', 'city', 'work_mode', 'status',)
    ORDERING_FIELDS = ('id', 'title', 'slug', 'description', 'type', 'contract_duration', 'experience_level', 'budget_min', 'budget_max', 'currency', 'budget_period', 'country', 'city', 'work_mode', 'start_date', 'deadline', 'status', 'published_at', 'views_count', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les offer, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les offer filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = Offer.objects.all()
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

    def get_by_id(self, offer_id: int) -> Optional[Offer]:
        """
        Obtenir un offer par ID.

        Args:
            offer_id (int): L'ID du offer

        Returns:
            Optional[Offer]: Le offer si trouvé, None sinon
        """
        return Offer.objects.filter(id=offer_id).first()

    def create(self, **kwargs) -> Offer:
        """
        Créer un nouveau offer.

        Args:
            **kwargs: Données du offer

        Returns:
            Offer: Le offer créé
        """
        required_skills = kwargs.pop('required_skills', None)
        offer = Offer.objects.create(**kwargs)
        if required_skills is not None:
            offer.required_skills.set(required_skills)
        return offer

    def update(self, offer: Offer, **kwargs) -> Offer:
        """
        Mettre à jour un offer existant.

        Args:
            offer (Offer): Le offer à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Offer: Le offer mis à jour
        """
        required_skills = kwargs.pop('required_skills', None)
        for field, value in kwargs.items():
            if hasattr(offer, field):
                setattr(offer, field, value)

        offer.save()
        if required_skills is not None:
            offer.required_skills.set(required_skills)
        return offer

    def delete(self, offer: Offer) -> bool:
        """
        Supprimer un offer.

        Args:
            offer (Offer): Le offer à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        offer.delete()
        return True

    def exists_by_id(self, offer_id: int) -> bool:
        """
        Vérifier si un offer existe par ID.

        Args:
            offer_id (int): L'ID du offer

        Returns:
            bool: True si le offer existe, False sinon
        """
        return Offer.objects.filter(id=offer_id).exists()