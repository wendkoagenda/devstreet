"""
Publication repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.communaute.models import Publication
from app.communaute.interfaces.publication_repository_interface import PublicationRepositoryInterface


class PublicationRepository(PublicationRepositoryInterface):
    """
    Implémentation concrète des opérations du repository publications.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('type', 'titre', 'description', 'lien_app', 'plateforme_app', 'contraintes', 'justification_finale', 'mode_vote',)
    ORDERING_FIELDS = ('id', 'type', 'titre', 'description', 'lien_app', 'plateforme_app', 'contraintes', 'justification_finale', 'decided_at', 'mode_vote', 'votes_fermes_at', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les publication, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les publication filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = Publication.objects.all()
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

    def get_by_id(self, publication_id: int) -> Optional[Publication]:
        """
        Obtenir un publication par ID.

        Args:
            publication_id (int): L'ID du publication

        Returns:
            Optional[Publication]: Le publication si trouvé, None sinon
        """
        return Publication.objects.filter(id=publication_id).first()

    def create(self, **kwargs) -> Publication:
        """
        Créer un nouveau publication.

        Args:
            **kwargs: Données du publication

        Returns:
            Publication: Le publication créé
        """
        return Publication.objects.create(**kwargs)

    def update(self, publication: Publication, **kwargs) -> Publication:
        """
        Mettre à jour un publication existant.

        Args:
            publication (Publication): Le publication à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Publication: Le publication mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(publication, field):
                setattr(publication, field, value)

        publication.save()
        return publication

    def delete(self, publication: Publication) -> bool:
        """
        Supprimer un publication.

        Args:
            publication (Publication): Le publication à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        publication.delete()
        return True

    def exists_by_id(self, publication_id: int) -> bool:
        """
        Vérifier si un publication existe par ID.

        Args:
            publication_id (int): L'ID du publication

        Returns:
            bool: True si le publication existe, False sinon
        """
        return Publication.objects.filter(id=publication_id).exists()