"""
LikeCommentaire repository implementation pour les opérations d'accès aux données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Q
from app.communaute.models import LikeCommentaire
from app.communaute.interfaces.likecommentaire_repository_interface import LikeCommentaireRepositoryInterface


class LikeCommentaireRepository(LikeCommentaireRepositoryInterface):
    """
    Implémentation concrète des opérations du repository likecommentaires.
    """

    # Champs sur lesquels porte la recherche textuelle (?search=) et champs autorisés pour le tri (?ordering=)
    SEARCH_FIELDS = ()
    ORDERING_FIELDS = ('id', 'created_at', 'updated_at',)

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les like_commentaire, avec recherche textuelle et tri facultatifs.

        Args:
            search (Optional[str]): Texte recherché (insensible à la casse) dans les champs texte
            ordering (Optional[str]): Champ de tri, préfixé par « - » pour l'ordre décroissant

        Returns:
            QuerySet: Les like_commentaire filtrés et triés (tri stable : l'ID départage les égalités)

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        queryset = LikeCommentaire.objects.all()
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

    def get_by_id(self, like_commentaire_id: int) -> Optional[LikeCommentaire]:
        """
        Obtenir un like_commentaire par ID.

        Args:
            like_commentaire_id (int): L'ID du like_commentaire

        Returns:
            Optional[LikeCommentaire]: Le like_commentaire si trouvé, None sinon
        """
        return LikeCommentaire.objects.filter(id=like_commentaire_id).first()

    def create(self, **kwargs) -> LikeCommentaire:
        """
        Créer un nouveau like_commentaire.

        Args:
            **kwargs: Données du like_commentaire

        Returns:
            LikeCommentaire: Le like_commentaire créé
        """
        return LikeCommentaire.objects.create(**kwargs)

    def update(self, like_commentaire: LikeCommentaire, **kwargs) -> LikeCommentaire:
        """
        Mettre à jour un like_commentaire existant.

        Args:
            like_commentaire (LikeCommentaire): Le like_commentaire à mettre à jour
            **kwargs: Données mises à jour

        Returns:
            LikeCommentaire: Le like_commentaire mis à jour
        """
        for field, value in kwargs.items():
            if hasattr(like_commentaire, field):
                setattr(like_commentaire, field, value)

        like_commentaire.save()
        return like_commentaire

    def delete(self, like_commentaire: LikeCommentaire) -> bool:
        """
        Supprimer un like_commentaire.

        Args:
            like_commentaire (LikeCommentaire): Le like_commentaire à supprimer

        Returns:
            bool: True si supprimé avec succès
        """
        like_commentaire.delete()
        return True

    def exists_by_id(self, like_commentaire_id: int) -> bool:
        """
        Vérifier si un like_commentaire existe par ID.

        Args:
            like_commentaire_id (int): L'ID du like_commentaire

        Returns:
            bool: True si le like_commentaire existe, False sinon
        """
        return LikeCommentaire.objects.filter(id=like_commentaire_id).exists()