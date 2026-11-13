"""
ConfirmationAide service layer pour les opérations de logique métier.
"""
from typing import Optional, Dict, Any
from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from app.communaute.models import Commentaire, ConfirmationAide
from app.communaute.repositories.confirmationaide_repository import ConfirmationAideRepository

User = get_user_model()


class ConfirmationAideService:
    """
    Classe de service pour la logique métier liée aux confirmation_aides.
    """

    def __init__(self):
        self.confirmationaide_repository = ConfirmationAideRepository()

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """Obtenir les confirmation_aides, avec recherche textuelle et tri facultatifs."""
        return self.confirmationaide_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, confirmation_aide_id: int) -> Optional[ConfirmationAide]:
        """Obtenir un confirmation_aide par ID."""
        return self.confirmationaide_repository.get_by_id(confirmation_aide_id)

    def _assert_cible_valide(self, commentaire: Commentaire) -> None:
        """Refuse toute confirmation hors réponse technique d'une entraide."""
        if commentaire.nature != 'REPONSE_TECHNIQUE':
            raise ValidationError(
                '« Ça m\'a aidé aussi » ne s\'applique qu\'aux réponses techniques.'
            )
        if commentaire.publication.type != 'ENTRAIDE':
            raise ValidationError(
                '« Ça m\'a aidé aussi » n\'est disponible que sur une entraide technique.'
            )

    def toggle(self, *, commentaire_id: int, membre: User) -> Dict[str, Any]:
        """
        Ajoute ou retire « Ça m'a aidé aussi » sur une réponse technique.
        Unique par membre et par commentaire.
        """
        commentaire = (
            Commentaire.objects.filter(id=commentaire_id)
            .select_related('publication')
            .first()
        )
        if commentaire is None:
            raise ValidationError('Réponse introuvable.')
        self._assert_cible_valide(commentaire)

        with transaction.atomic():
            existing = (
                ConfirmationAide.objects.select_for_update()
                .filter(commentaire_id=commentaire_id, membre_id=membre.id)
                .first()
            )
            if existing:
                existing.delete()
                confirmed = False
            else:
                try:
                    ConfirmationAide.objects.create(
                        commentaire=commentaire,
                        membre=membre,
                        created_by=membre.id,
                        updated_by=membre.id,
                    )
                    confirmed = True
                except IntegrityError:
                    # Course concurrente : l'autre requête a déjà créé la confirmation
                    confirmed = True

            confirmations_count = ConfirmationAide.objects.filter(
                commentaire_id=commentaire_id
            ).count()

        return {
            'confirmed': confirmed,
            'confirmations_count': confirmations_count,
            'commentaire_id': commentaire_id,
        }

    def create(self, confirmation_aide_data: Dict[str, Any]) -> ConfirmationAide:
        """Création directe interdite : passer par toggle()."""
        raise ValidationError(
            'Utilisez POST /commentaires/{id}/confirmation-aide pour confirmer une aide.'
        )

    def update(
        self,
        confirmation_aide_id: int,
        confirmation_aide_data: Dict[str, Any],
        partial: bool = False,
    ) -> Optional[ConfirmationAide]:
        """Mise à jour directe interdite."""
        raise ValidationError(
            'Utilisez POST /commentaires/{id}/confirmation-aide pour modifier une confirmation.'
        )

    def delete(self, confirmation_aide_id: int) -> bool:
        """Supprimer un confirmation_aide (réservé aux opérations internes / admin)."""
        confirmation_aide = self.confirmationaide_repository.get_by_id(confirmation_aide_id)
        if not confirmation_aide:
            return False
        return self.confirmationaide_repository.delete(confirmation_aide)

    def validate_data(self, confirmation_aide_data: Dict[str, Any]):
        """Valider les données du confirmation_aide."""
        commentaire = confirmation_aide_data.get('commentaire')
        commentaire_id = confirmation_aide_data.get('commentaire_id')
        if commentaire is None and commentaire_id is None:
            raise ValidationError('Le commentaire est obligatoire.')
        if not confirmation_aide_data.get('membre') and not confirmation_aide_data.get('membre_id'):
            raise ValidationError('Le membre est obligatoire.')

        if commentaire is None and commentaire_id is not None:
            commentaire = (
                Commentaire.objects.filter(id=commentaire_id)
                .select_related('publication')
                .first()
            )
            if commentaire is None:
                raise ValidationError('Réponse introuvable.')
        if commentaire is not None:
            if not hasattr(commentaire, 'publication'):
                commentaire = (
                    Commentaire.objects.filter(id=commentaire.id)
                    .select_related('publication')
                    .first()
                )
            if commentaire is None:
                raise ValidationError('Réponse introuvable.')
            self._assert_cible_valide(commentaire)
