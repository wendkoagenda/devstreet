"""Réputation DevStreet calculée à la volée (UC-02).

Agrège avis marketplace, réponses forum acceptées, confirmations d'aide,
contributions hub acceptées et apps partagées. Aucun champ stocké.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from django.db.models import Avg, Count

from app.marketplace.models import Review
from app.marketplace.services.me_service import MeService

# Pondération MVP (somme 100) — ajustable sans migration
WEIGHTS = {
    "reviews": 50,
    "forum": 25,
    "hub": 15,
    "code_shares": 10,
}

# Seuils pour saturer chaque axe (points = weight * min(1, count/cap) ou avg/5 pour reviews)
CAPS = {
    "reviews_count": 5,
    "accepted_answers": 10,
    "help_confirmations": 20,
    "accepted_contributions": 5,
    "applications": 5,
}


def _clamp_points(weight: int, ratio: float) -> int:
    return max(0, min(weight, round(weight * max(0.0, min(1.0, ratio)))))


class ReputationService:
    """Calcule le score de réputation d'un utilisateur DevStreet."""

    @classmethod
    def for_user(cls, user) -> Dict[str, Any]:
        profil = MeService.get_profil(user)
        return cls.build(user, profil_id=profil.id if profil else None)

    @classmethod
    def for_profil(cls, profil) -> Dict[str, Any]:
        return cls.build(profil.user, profil_id=profil.id)

    @classmethod
    def build(cls, user, *, profil_id: Optional[int] = None) -> Dict[str, Any]:
        reviews = cls._reviews(profil_id)
        forum = cls._forum(user)
        hub = cls._hub(user)
        code = cls._code_shares(user)

        review_ratio = (reviews["avg"] / 5.0) if reviews["avg"] is not None else 0.0
        if reviews["count"] == 0:
            review_ratio = 0.0
        # Bonus volume léger : moyenne * min(1, count/cap)
        review_volume = min(1.0, reviews["count"] / CAPS["reviews_count"]) if reviews["count"] else 0.0
        review_points = _clamp_points(WEIGHTS["reviews"], review_ratio * (0.5 + 0.5 * review_volume))

        forum_ratio = min(
            1.0,
            (forum["accepted_answers"] / CAPS["accepted_answers"]) * 0.7
            + (forum["help_confirmations"] / CAPS["help_confirmations"]) * 0.3,
        )
        forum_points = _clamp_points(WEIGHTS["forum"], forum_ratio)

        hub_points = _clamp_points(
            WEIGHTS["hub"],
            hub["accepted_contributions"] / CAPS["accepted_contributions"],
        )
        code_points = _clamp_points(
            WEIGHTS["code_shares"],
            code["applications"] / CAPS["applications"],
        )

        score = min(100, review_points + forum_points + hub_points + code_points)
        return {
            "score": score,
            "rating_avg": reviews["avg"],
            "reviews_count": reviews["count"],
            "breakdown": {
                "reviews": {
                    "label": "Avis missions",
                    "count": reviews["count"],
                    "avg": reviews["avg"],
                    "points": review_points,
                    "max": WEIGHTS["reviews"],
                },
                "forum": {
                    "label": "Forum",
                    "accepted_answers": forum["accepted_answers"],
                    "help_confirmations": forum["help_confirmations"],
                    "points": forum_points,
                    "max": WEIGHTS["forum"],
                },
                "hub": {
                    "label": "Contributions code",
                    "accepted_contributions": hub["accepted_contributions"],
                    "points": hub_points,
                    "max": WEIGHTS["hub"],
                },
                "code_shares": {
                    "label": "Apps partagées",
                    "applications": code["applications"],
                    "points": code_points,
                    "max": WEIGHTS["code_shares"],
                },
            },
        }

    @staticmethod
    def _reviews(profil_id: Optional[int]) -> dict:
        if not profil_id:
            return {"avg": None, "count": 0}
        stats = Review.objects.filter(target_id=profil_id, is_public=True).aggregate(
            avg=Avg("rating"), total=Count("id")
        )
        average = round(float(stats["avg"]), 1) if stats["avg"] is not None else None
        return {"avg": average, "count": stats["total"] or 0}

    @staticmethod
    def _forum(user) -> dict:
        from app.communaute.models import ConfirmationAide, Publication
        accepted = Publication.objects.filter(reponse_acceptee__auteur=user).count()
        helps = ConfirmationAide.objects.filter(commentaire__auteur=user).exclude(membre=user).count()
        return {"accepted_answers": accepted, "help_confirmations": helps}

    @staticmethod
    def _hub(user) -> dict:
        from app.devstreet_hub.models import Contribution
        count = Contribution.objects.filter(author=user, status="accepted").count()
        return {"accepted_contributions": count}

    @staticmethod
    def _code_shares(user) -> dict:
        from app.communaute.models import Publication
        apps = Publication.objects.filter(auteur=user, type="APPLICATION").count()
        return {"applications": apps}
