"""Dépôt d'avis après une candidature acceptée (UC-12)."""
from typing import Any, Dict, List

from django.db import transaction
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from app.marketplace.models import Candidature, Review
from app.marketplace.services.me_service import MeService


def review_dict(row: Review) -> dict:
    return {
        "id": row.id,
        "rating": row.rating,
        "comment": row.comment,
        "is_public": row.is_public,
        "created_at": row.created_at.isoformat(),
        "target": {
            "id": row.target_id,
            "name": row.target.user.full_name or row.target.user.email,
        },
        "candidature_id": row.candidature_id,
    }


class ReviewMeService:
    """Avis laissés par le profil connecté, liés à une mission acceptée."""

    @staticmethod
    def _profil(user):
        profil = MeService.get_profil(user)
        if profil is None:
            raise PermissionDenied("Créez d'abord votre profil marketplace.")
        return profil

    @classmethod
    def list_mine(cls, user) -> List[dict]:
        profil = cls._profil(user)
        rows = (
            Review.objects.filter(author=profil)
            .select_related("target__user")
            .order_by("-created_at")
        )
        return [review_dict(row) for row in rows]

    @classmethod
    def pending(cls, user) -> List[dict]:
        """Candidatures acceptées où je peux encore noter l'autre partie."""
        profil = cls._profil(user)
        already = set(
            Review.objects.filter(author=profil, candidature_id__isnull=False).values_list(
                "candidature_id", flat=True
            )
        )
        # Candidat : missions acceptées
        as_candidate = (
            Candidature.objects.filter(profil=profil, status="accepted")
            .select_related("offer__company", "offer__recruiter__user")
            .order_by("-decided_at")
        )
        # Recruteur : candidatures acceptées sur les offres de mon entreprise
        as_recruiter = (
            Candidature.objects.filter(
                offer__company_id=profil.company_id, status="accepted"
            )
            .exclude(profil=profil)
            .select_related("profil__user", "offer")
            .order_by("-decided_at")
            if profil.company_id
            else Candidature.objects.none()
        )

        rows = []
        for candidature in list(as_candidate) + list(as_recruiter):
            if candidature.id in already:
                continue
            if candidature.profil_id == profil.id:
                # Je suis le talent : noter le recruteur (ou l'entreprise via le recruteur)
                target = candidature.offer.recruiter
                role = "candidate"
            else:
                target = candidature.profil
                role = "recruiter"
            if target is None:
                continue
            rows.append(
                {
                    "candidature_id": candidature.id,
                    "role": role,
                    "offer": {
                        "id": candidature.offer_id,
                        "title": candidature.offer.title,
                    },
                    "target": {
                        "id": target.id,
                        "name": target.user.full_name or target.user.email,
                        "headline": target.headline,
                    },
                    "decided_at": candidature.decided_at.isoformat() if candidature.decided_at else None,
                }
            )
        return rows

    @classmethod
    @transaction.atomic
    def create(cls, user, data: Dict[str, Any]) -> dict:
        profil = cls._profil(user)
        candidature_id = data.get("candidature_id")
        candidature = (
            Candidature.objects.select_related("offer__recruiter", "profil__user", "offer")
            .filter(id=candidature_id, status="accepted")
            .first()
        )
        if candidature is None:
            raise NotFound("Mission introuvable ou non acceptée.")

        if candidature.profil_id == profil.id:
            target = candidature.offer.recruiter
        elif profil.company_id and candidature.offer.company_id == profil.company_id:
            target = candidature.profil
        else:
            raise PermissionDenied("Vous ne pouvez pas noter cette mission.")

        if target is None or target.id == profil.id:
            raise ValidationError({"error": "Cible d'avis invalide."})

        if Review.objects.filter(author=profil, candidature=candidature).exists():
            raise ValidationError({"error": "Vous avez déjà noté cette mission."})

        row = Review.objects.create(
            author=profil,
            target=target,
            candidature=candidature,
            rating=data["rating"],
            comment=data.get("comment") or "",
            is_public=data.get("is_public", True),
            created_by=user.id,
            updated_by=user.id,
        )
        return review_dict(row)
