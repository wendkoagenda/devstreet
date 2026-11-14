"""
Pagination commune des listes de l'API : 20 éléments par page, 100 au maximum (?page_size=...).
"""
from rest_framework.pagination import CursorPagination, PageNumberPagination


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class FeedCursorPagination(CursorPagination):
    """
    Pagination par curseur pour le fil d'actualité (scroll infini).
    Tri stable créé_at + id pour éviter les doublons / trous.
    """

    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    ordering = ('-created_at', '-id')
    cursor_query_param = 'cursor'


class PourVousCursorPagination(FeedCursorPagination):
    """
    Fil « Pour vous » : thèmes / abonnements priorisés puis le reste.
    """

    ordering = ('-priorite', '-created_at', '-id')


class PopulairesCursorPagination(FeedCursorPagination):
    """
    Fil « Populaires » : engagement (likes + commentaires) puis chronologie.
    """

    ordering = ('-likes_count', '-comments_count', '-created_at', '-id')
