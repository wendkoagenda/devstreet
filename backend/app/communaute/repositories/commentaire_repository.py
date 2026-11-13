"""
Commentaire repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.communaute.models import Commentaire
from app.communaute.interfaces.commentaire_repository_interface import CommentaireRepositoryInterface


class CommentaireRepository(CommentaireRepositoryInterface):
    """
    Implémentation concrète des opérations du repository commentaires.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ('nature', 'texte',)
    ORDERING_FIELDS = ('id', 'nature', 'texte', 'est_anonyme', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les commentaire, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les commentaire filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = Commentaire.objects.all()
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

    def get_by_id(self, commentaire_id: int) -> Optional[Commentaire]:
        """
        Obtenir un commentaire par ID.

        Args:
            commentaire_id (int): L'ID du commentaire

        Returns:
            Optional[Commentaire]: Le commentaire si trouvé, None sinon
        """
        return Commentaire.objects.filter(id=commentaire_id).first()

    def create(self, **kwargs) -> Commentaire:
        """
        Créer un nouveau commentaire.

        Args:
            **kwargs: Données du commentaire

        Returns:
            Commentaire: Le commentaire créé
        """
        return Commentaire.objects.create(**kwargs)

    def update(self, commentaire: Commentaire, **kwargs) -> Commentaire:
        """
        Mettre à jour un commentaire existant.

        Args:
            commentaire (Commentaire): Le commentaire à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            Commentaire: Le commentaire mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(commentaire, field):
                setattr(commentaire, field, value)

        commentaire.save()
        return commentaire

    def delete(self, commentaire: Commentaire) -> bool:
        """
        Supprimer un commentaire.

        Args:
            commentaire (Commentaire): Le commentaire à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        commentaire.delete()
        return True

    def exists_by_id(self, commentaire_id: int) -> bool:
        """
        Vérifier si un commentaire existe par ID.

        Args:
            commentaire_id (int): L'ID du commentaire

        Returns:
            bool: True si le commentaire existe, False sinon
        """
        return Commentaire.objects.filter(id=commentaire_id).exists()