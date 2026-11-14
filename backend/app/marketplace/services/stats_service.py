"""Petites statistiques affichées en haut des pages de la marketplace (une ligne de pastilles par page).

Chaque « scope » correspond à une page et ne calcule que ce dont elle a besoin. Toutes les données sont celles du
membre connecté : rien n'est agrégé au niveau de la plateforme (c'est le rôle de l'administration).

Les statistiques « candidat » viennent du profil dev, celles « recruteur » du profil entreprise.
"""
from datetime import date, timedelta
from typing import Callable, Dict, Optional

from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from app.marketplace.models import Availability, Candidature, Connection, Experience, Offer, Profil, Review, Swipe
from app.marketplace.services.market_service import MarketService
from app.marketplace.services.me_service import MeService

STATUSES = ("sent", "shortlisted", "accepted", "rejected")
AVAILABILITY_PRIORITY = ("busy", "leave", "partial", "available")
# Score à partir duquel une offre est considérée comme bien adaptée au profil
WELL_MATCHED_SCORE = 70


def _status_counts(queryset) -> Dict[str, int]:
    """Nombre de candidatures par statut (tous les statuts présents, même à zéro) et total."""
    counts = {status: 0 for status in STATUSES}
    for row in queryset.values("status").annotate(total=Count("id")):
        counts[row["status"]] = row["total"]
    counts["total"] = sum(counts[status] for status in STATUSES)
    return counts


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


def _reputation(profil: Profil) -> dict:
    stats = Review.objects.filter(target=profil, is_public=True).aggregate(avg=Avg("rating"), total=Count("id"))
    average = round(float(stats["avg"]), 1) if stats["avg"] is not None else None
    return {"rating_avg": average, "reviews_count": stats["total"]}


def _availability(profil: Profil, today: date) -> dict:
    """
    Statut du jour (statut le plus contraignant parmi les périodes en cours), prochaine disponibilité et missions.

    Sans période, le membre est disponible. Seules les périodes occupées comptent : s'il est occupé ou en congé
    aujourd'hui, il redevient disponible le lendemain de la fin des périodes occupées qui s'enchaînent.
    """
    periods = list(Availability.objects.filter(profil=profil, end_date__gte=today).order_by("start_date"))
    covering = [period for period in periods if period.start_date <= today]
    current: Optional[Availability] = next(
        (period for status in AVAILABILITY_PRIORITY for period in covering if period.status == status), None
    )
    next_free: Optional[date] = None
    if current is not None and current.status in ("busy", "leave"):
        blocking = [p for p in periods if p.status in ("busy", "leave")]
        end = max(p.end_date for p in blocking if p.start_date <= today)
        extended = True
        while extended:
            extended = False
            for period in blocking:
                if period.start_date <= end + timedelta(days=1) and period.end_date > end:
                    end, extended = period.end_date, True
        next_free = end + timedelta(days=1)
    return {
        "current": (
            {"status": current.status, "end_date": current.end_date.isoformat(), "source": current.source, "note": current.note}
            if current
            else None
        ),
        "next_available_start": next_free.isoformat() if next_free else None,
        "periods_count": len(periods),
        "upcoming_missions": sum(1 for period in periods if period.source == "mission"),
    }


def connections_count(user) -> int:
    """Connexions du membre, avec son profil dev comme avec son profil entreprise."""
    mine = list(Profil.objects.filter(user=user).values_list("id", flat=True))
    return Connection.objects.filter(Q(profil_a_id__in=mine) | Q(profil_b_id__in=mine), status="matched").count()


class StatsService:
    """Statistiques par page."""

    @staticmethod
    def _dev(user) -> Profil:
        profil = MeService.get_profil(user)
        if profil is None:
            raise PermissionDenied("Créez d'abord votre profil dev.")
        return profil

    @staticmethod
    def _entreprise(user) -> Profil:
        profil = MeService.get_entreprise_profil(user)
        if profil is None:
            raise PermissionDenied("Réservé aux membres d'une entreprise.")
        return profil

    # ── Entreprise ───────────────────────────────────────────────────────────

    @classmethod
    def offers(cls, user) -> dict:
        """Mes offres : offres par statut, candidatures à traiter, vues."""
        company_id = cls._entreprise(user).company_id
        offers = Offer.objects.filter(company_id=company_id)
        counts = {"open": 0, "draft": 0, "closed": 0}
        for row in offers.values("status").annotate(total=Count("id")):
            counts[row["status"]] = row["total"]
        return {
            **counts,
            "total": sum(counts.values()),
            "to_process": Candidature.objects.filter(offer__company_id=company_id, status="sent").count(),
            "views_total": offers.aggregate(total=Sum("views_count"))["total"] or 0,
        }

    @classmethod
    def _pool(cls, user):
        company_id = cls._entreprise(user).company_id
        return Swipe.objects.filter(author__company_id=company_id, context="recruit", direction="like"), company_id

    @classmethod
    def pool(cls, user) -> dict:
        """Vivier : talents gardés, ajoutés cette semaine, ouverts aux opportunités."""
        likes, _company_id = cls._pool(user)
        week_ago = timezone.now() - timedelta(days=7)
        return {
            "total": likes.values("target_id").distinct().count(),
            "this_week": likes.filter(created_at__gte=week_ago).values("target_id").distinct().count(),
            "open_to_work": likes.filter(target__is_open_to_work=True).values("target_id").distinct().count(),
        }

    # ── Dev ──────────────────────────────────────────────────────────────────

    @classmethod
    def applications(cls, user) -> dict:
        """Mes candidatures : par statut, et missions à venir."""
        profil = cls._dev(user)
        today = timezone.localdate()
        missions = Availability.objects.filter(profil=profil, source="mission", end_date__gte=today).count()
        return {**_status_counts(Candidature.objects.filter(profil=profil)), "upcoming_missions": missions}

    @classmethod
    def availability(cls, user) -> dict:
        """Mes disponibilités : statut du jour, prochaine disponibilité, missions à venir."""
        return _availability(cls._dev(user), timezone.localdate())

    @classmethod
    def cv(cls, user) -> dict:
        """Mon CV : complétude du profil et éléments manquants."""
        return {"completeness": _completeness(cls._dev(user))}

    @classmethod
    def profile(cls, user) -> dict:
        """Résumé pour « mon profil pro » (orbite) : disponibilité, avis et connexions."""
        profil = cls._dev(user)
        return {
            "availability": _availability(profil, timezone.localdate()),
            "reputation": _reputation(profil),
            "connections_count": connections_count(user),
        }

    # ── Général ──────────────────────────────────────────────────────────────

    @classmethod
    def explore(cls, user) -> dict:
        """Explorer les offres : offres ouvertes, bien adaptées à mon profil, candidatures envoyées."""
        company_id = MeService.company_id_of(user.id)
        open_offers = Offer.objects.filter(status="open")
        if company_id:
            open_offers = open_offers.exclude(company_id=company_id)
        profil = MeService.get_profil(user)
        if profil is None:
            return {"open_offers": open_offers.count(), "well_matched": None, "applications_sent": 0}
        # Le score se calcule sur les offres affichées (les plus récentes), comme la page elle-même
        matched = sum(1 for row in MarketService.list_open_offers(user) if row["score"] >= WELL_MATCHED_SCORE)
        return {
            "open_offers": open_offers.count(),
            "well_matched": matched,
            "applications_sent": Candidature.objects.filter(profil=profil).count(),
        }

    @classmethod
    def network(cls, user) -> dict:
        """
        Réseau : connexions, demandes envoyées en attente d'une réponse, demandes reçues (des profils qui ont
        proposé de se connecter et à qui je n'ai pas encore répondu). Compté avec le profil dev comme avec le profil entreprise.
        """
        mine = list(Profil.objects.filter(user=user).values_list("id", flat=True))
        if not mine:
            raise PermissionDenied("Créez d'abord votre profil marketplace.")
        connected = set()
        for a_id, b_id in Connection.objects.filter(
            Q(profil_a_id__in=mine) | Q(profil_b_id__in=mine), status="matched"
        ).values_list("profil_a_id", "profil_b_id"):
            connected.add(b_id if a_id in mine else a_id)
        network = Swipe.objects.filter(context="network")
        sent = set(network.filter(author_id__in=mine, direction="like").values_list("target_id", flat=True))
        answered = set(network.filter(author_id__in=mine).values_list("target_id", flat=True))
        received = set(network.filter(target_id__in=mine, direction="like").values_list("author_id", flat=True))
        return {
            "connections": len(connected),
            "pending_sent": len(sent - connected),
            "pending_received": len(received - answered - connected),
        }

    # ── Aiguillage ───────────────────────────────────────────────────────────

    SCOPES: Dict[str, Callable] = {}

    @classmethod
    def get(cls, user, scope: Optional[str]) -> dict:
        handler = cls.SCOPES.get(scope or "")
        if handler is None:
            raise ValidationError({"scope": f"Valeur invalide ({', '.join(sorted(cls.SCOPES))})."})
        return handler(user)


StatsService.SCOPES = {
    "offers": StatsService.offers,
    "pool": StatsService.pool,
    "applications": StatsService.applications,
    "availability": StatsService.availability,
    "cv": StatsService.cv,
    "profile": StatsService.profile,
    "explore": StatsService.explore,
    "network": StatsService.network,
}
