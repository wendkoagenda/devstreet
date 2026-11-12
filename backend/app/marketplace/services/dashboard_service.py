"""Tableau de bord de l'utilisateur connecté : indicateurs de son profil, de ses candidatures et, s'il recrute, de son entreprise.

Toutes les données sont celles de l'utilisateur ; rien n'est agrégé au niveau de la plateforme (c'est le rôle de l'administration).
"""
from datetime import date, timedelta
from typing import Dict, List, Optional

from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from app.marketplace.models import Availability, Candidature, Connection, Experience, Offer, Profil, Review, Swipe
from app.marketplace.presenters import candidature_dict, profil_card
from app.marketplace.services.market_service import MarketService
from app.marketplace.services.me_service import MeService
from app.marketplace.services.scoring import build_contexts, compute_score

STATUSES = ("sent", "shortlisted", "accepted", "rejected")
WEEKS = 8
AVAILABILITY_PRIORITY = ("busy", "leave", "partial", "available")


def _status_counts(queryset) -> Dict[str, int]:
    """Nombre de candidatures par statut (tous les statuts présents, même à zéro) et total."""
    counts = {status: 0 for status in STATUSES}
    for row in queryset.values("status").annotate(total=Count("id")):
        counts[row["status"]] = row["total"]
    counts["total"] = sum(counts[status] for status in STATUSES)
    return counts


class DashboardService:
    """Construit les blocs du tableau de bord."""

    @classmethod
    def build(cls, user) -> dict:
        profil = MeService.get_profil(user)
        if profil is None:
            raise PermissionDenied("Créez d'abord votre profil marketplace.")
        today = timezone.localdate()
        return {
            "profil": {"id": profil.id, "name": user.full_name or user.email.split("@")[0], "headline": profil.headline},
            "completeness": cls._completeness(profil),
            "reputation": cls._reputation(profil),
            "availability": cls._availability(profil, today),
            "connections_count": Connection.objects.filter(Q(profil_a=profil) | Q(profil_b=profil), status="matched").count(),
            "candidate": cls._candidate(user, profil, today),
            "recruiter": cls._recruiter(profil, today) if profil.company_id else None,
        }

    # ── Profil ───────────────────────────────────────────────────────────────

    @staticmethod
    def _completeness(profil: Profil) -> dict:
        """Complétude du profil : une case par élément qui améliore les recommandations et le CV."""
        checks = [
            ("headline", "Accroche", bool(profil.headline)),
            ("bio", "Présentation", bool(profil.bio)),
            ("city", "Ville", bool(profil.city)),
            ("languages", "Langues", bool(profil.languages)),
            ("skills", "Au moins 3 compétences", profil.profil_skills.count() >= 3),
            ("experiences", "Une expérience", Experience.objects.filter(profil=profil).exists()),
            ("links", "Un lien (GitHub, LinkedIn, portfolio)", bool(profil.github_url or profil.linkedin_url or profil.portfolio_url)),
            ("daily_rate", "Tarif journalier", profil.daily_rate is not None),
        ]
        done = sum(1 for _key, _label, ok in checks if ok)
        return {
            "percent": round(100 * done / len(checks)),
            "missing": [{"key": key, "label": label} for key, label, ok in checks if not ok],
        }

    @staticmethod
    def _reputation(profil: Profil) -> dict:
        stats = Review.objects.filter(target=profil, is_public=True).aggregate(avg=Avg("rating"), total=Count("id"))
        average = round(float(stats["avg"]), 1) if stats["avg"] is not None else None
        return {"rating_avg": average, "reviews_count": stats["total"]}

    @staticmethod
    def _availability(profil: Profil, today: date) -> dict:
        """Statut du jour (statut le plus contraignant parmi les périodes en cours) et prochaine période libre."""
        periods = list(Availability.objects.filter(profil=profil, end_date__gte=today).order_by("start_date"))
        covering = [period for period in periods if period.start_date <= today]
        current: Optional[Availability] = next(
            (period for status in AVAILABILITY_PRIORITY for period in covering if period.status == status), None
        )
        upcoming = next((p for p in periods if p.start_date > today and p.status in ("available", "partial")), None)
        return {
            "current": (
                {"status": current.status, "end_date": current.end_date.isoformat(), "source": current.source, "note": current.note}
                if current
                else None
            ),
            "next_available_start": upcoming.start_date.isoformat() if upcoming else None,
            "periods_count": len(periods),
        }

    # ── Candidat ─────────────────────────────────────────────────────────────

    @classmethod
    def _candidate(cls, user, profil: Profil, today: date) -> dict:
        mine = Candidature.objects.filter(profil=profil)
        recent = mine.select_related("offer__company").prefetch_related("offer__required_skills").order_by("-created_at")[:5]
        missions = Availability.objects.filter(profil=profil, source="mission", end_date__gte=today).order_by("start_date")
        return {
            "counts": _status_counts(mine),
            "recent": [candidature_dict(row, with_offer=True) for row in recent],
            "recommended_offers": MarketService.list_open_offers(user)[:3],
            "upcoming_missions": [
                {"id": row.id, "note": row.note, "start_date": row.start_date.isoformat(), "end_date": row.end_date.isoformat()}
                for row in missions
            ],
        }

    # ── Recruteur ────────────────────────────────────────────────────────────

    @classmethod
    def _recruiter(cls, profil: Profil, today: date) -> dict:
        company = profil.company
        offers = Offer.objects.filter(company_id=profil.company_id)
        received = Candidature.objects.filter(offer__company_id=profil.company_id)
        offer_counts = {"open": 0, "draft": 0, "closed": 0}
        for row in offers.values("status").annotate(total=Count("id")):
            offer_counts[row["status"]] = row["total"]
        offer_counts["total"] = sum(offer_counts.values())

        top = (
            offers.annotate(
                candidatures_total=Count("candidatures", distinct=True),
                candidatures_new=Count("candidatures", filter=Q(candidatures__status="sent"), distinct=True),
            )
            .filter(candidatures_total__gt=0)
            .order_by("-candidatures_total", "-id")[:3]
        )
        pool_size = (
            Swipe.objects.filter(author__company_id=profil.company_id, context="recruit", direction="like")
            .values("target_id")
            .distinct()
            .count()
        )
        return {
            "company": {"id": company.id, "name": company.name, "is_verified": company.is_verified},
            "offers": offer_counts,
            "views_total": offers.aggregate(total=Sum("views_count"))["total"] or 0,
            "candidatures": _status_counts(received),
            "pool_size": pool_size,
            "top_offers": [
                {
                    "id": offer.id,
                    "title": offer.title,
                    "status": offer.status,
                    "candidatures_count": offer.candidatures_total,
                    "candidatures_new": offer.candidatures_new,
                }
                for offer in top
            ],
            "recent_candidatures": cls._recent_received(received),
            "weekly": cls._weekly(received, today),
        }

    @staticmethod
    def _recent_received(received) -> List[dict]:
        rows = list(
            received.select_related("profil__user", "offer__company")
            .prefetch_related("profil__profil_skills__skill", "offer__required_skills")
            .order_by("-created_at")[:5]
        )
        contexts = build_contexts([row.profil for row in rows])
        result = []
        for row in rows:
            ctx = contexts[row.profil_id]
            data = candidature_dict(row)
            data["score"] = compute_score(row.offer, row.profil, ctx)["score"]
            data["offer"] = {"id": row.offer_id, "title": row.offer.title}
            data["profil"] = profil_card(row.profil, ctx)
            result.append(data)
        return result

    @staticmethod
    def _weekly(received, today: date) -> List[dict]:
        """Candidatures reçues par semaine (lundi au dimanche) sur les dernières semaines, la plus ancienne d'abord."""
        this_monday = today - timedelta(days=today.weekday())
        first = this_monday - timedelta(weeks=WEEKS - 1)
        buckets = [0] * WEEKS
        for created_at in received.filter(created_at__date__gte=first).values_list("created_at", flat=True):
            index = (timezone.localtime(created_at).date() - first).days // 7
            if 0 <= index < WEEKS:
                buckets[index] += 1
        return [{"week_start": (first + timedelta(weeks=index)).isoformat(), "count": count} for index, count in enumerate(buckets)]
