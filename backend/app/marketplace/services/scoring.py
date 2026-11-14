"""Score de recommandation d'une offre pour un profil, calculé par règles (sur 100).

Pas d'IA ici : la part « IA » du score est prévue plus tard (embeddings). Chaque critère renvoie un score et un
court détail affichable (« Pourquoi cette offre ? »). Les contextes de profils (compétences, calendrier, avis) sont
chargés en lot pour éviter une requête par profil.
"""
import calendar
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, Iterable, List, Optional

from django.db.models import Avg, Count

from app.marketplace.models import Availability, Offer, Profil, ProfilSkill, Review

WEIGHTS = {
    "skills": 40,
    "experience": 15,
    "location": 15,
    "budget": 10,
    "availability": 10,
    "reputation": 10,
}
LABELS = {
    "skills": "Compétences",
    "experience": "Expérience",
    "location": "Localisation",
    "budget": "Budget",
    "availability": "Disponibilité",
    "reputation": "Réputation",
}
# Années d'expérience attendues par niveau (minimum)
LEVEL_MIN_YEARS = {"junior": 0, "mid": 2, "senior": 5, "expert": 8}
WORKING_DAYS_PER_MONTH = 22


@dataclass
class ProfilContext:
    """Données d'un profil nécessaires au calcul (chargées en lot)."""

    skill_levels: Dict[int, int] = field(default_factory=dict)
    availabilities: List[Availability] = field(default_factory=list)
    rating_avg: Optional[float] = None
    reviews_count: int = 0


def add_months(start: date, months: int) -> date:
    """Ajoute des mois à une date (le jour est ramené à la fin du mois si besoin)."""
    index = start.month - 1 + months
    year, month = start.year + index // 12, index % 12 + 1
    return date(year, month, min(start.day, calendar.monthrange(year, month)[1]))


HOURS_PER_DAY = 8


def mission_period(start: date, duration: Optional[int], offer_type: str, unit: str = "month") -> tuple:
    """
    Période (début, fin incluse) d'une mission selon sa durée et son unité (heures, jours, mois, années).

    Les heures sont converties en jours de travail (8 h par jour, arrondi au jour supérieur).
    Sans durée : 12 mois pour un CDI/CDD, 1 mois sinon.
    """
    if not duration:
        duration, unit = (12 if offer_type in ("cdi", "cdd") else 1), "month"
    if unit == "hour":
        days = max(1, -(-duration // HOURS_PER_DAY))
        return start, start + timedelta(days=days - 1)
    if unit == "day":
        return start, start + timedelta(days=duration - 1)
    months = duration * 12 if unit == "year" else duration
    return start, add_months(start, months) - timedelta(days=1)


def offer_period(offer: Offer) -> Optional[tuple]:
    """Période de mission de l'offre ; None si elle n'a pas de date de début."""
    if not offer.start_date:
        return None
    return mission_period(offer.start_date, offer.contract_duration, offer.type, offer.contract_duration_unit)


def build_contexts(profils: Iterable[Profil]) -> Dict[int, ProfilContext]:
    """Charge en 3 requêtes les compétences, périodes de calendrier et avis publics des profils."""
    contexts = {profil.id: ProfilContext() for profil in profils}
    ids = list(contexts)
    if not ids:
        return contexts
    for row in ProfilSkill.objects.filter(profil_id__in=ids).values("profil_id", "skill_id", "level"):
        contexts[row["profil_id"]].skill_levels[row["skill_id"]] = row["level"]
    for availability in Availability.objects.filter(profil_id__in=ids):
        contexts[availability.profil_id].availabilities.append(availability)
    reviews = (
        Review.objects.filter(target_id__in=ids, is_public=True)
        .values("target_id")
        .annotate(avg=Avg("rating"), total=Count("id"))
    )
    for row in reviews:
        contexts[row["target_id"]].rating_avg = float(row["avg"])
        contexts[row["target_id"]].reviews_count = row["total"]
    return contexts


def _skills(offer: Offer, profil: Profil, ctx: ProfilContext, required_ids: List[int]):
    if not required_ids:
        return WEIGHTS["skills"], "Aucune compétence requise"
    points = 0.0
    matched = 0
    for skill_id in required_ids:
        level = ctx.skill_levels.get(skill_id)
        if level:
            matched += 1
            points += 0.6 + 0.4 * (level - 1) / 4
    return WEIGHTS["skills"] * points / len(required_ids), f"{matched} compétence(s) sur {len(required_ids)}"


def _experience(offer: Offer, profil: Profil, ctx: ProfilContext):
    needed = LEVEL_MIN_YEARS.get(offer.experience_level, 0)
    years = profil.years_of_experience
    if years >= needed:
        return WEIGHTS["experience"], f"{years} an(s), {needed} attendu(s)"
    return WEIGHTS["experience"] * years / needed, f"{years} an(s), {needed} attendu(s)"


def _location(offer: Offer, profil: Profil, ctx: ProfilContext):
    max_points = WEIGHTS["location"]
    if offer.work_mode == "remote":
        if profil.remote:
            return max_points, "Télétravail"
        return (9 if _same_country(offer, profil) else 4), "Télétravail souhaité"
    same_country = _same_country(offer, profil)
    same_city = same_country and bool(offer.city) and offer.city.strip().lower() == profil.city.strip().lower()
    if same_city:
        return max_points, f"Même ville ({offer.city})"
    if same_country:
        return (10 if offer.work_mode == "hybrid" else 8), "Même pays"
    if offer.work_mode == "hybrid" and profil.remote:
        return 5, "Autre pays, télétravail possible"
    return 0, "Autre pays"


def _same_country(offer: Offer, profil: Profil) -> bool:
    return offer.country.upper() == profil.country.upper()


def _budget(offer: Offer, profil: Profil, ctx: ProfilContext):
    neutral = WEIGHTS["budget"] / 2
    budget = offer.budget_max or offer.budget_min
    if not budget or not profil.daily_rate or offer.currency != profil.currency:
        return neutral, "Budget non comparable"
    if offer.budget_period == "day":
        daily_budget = float(budget)
    elif offer.budget_period == "month":
        daily_budget = float(budget) / WORKING_DAYS_PER_MONTH
    else:
        return neutral, "Forfait : non comparable"
    ratio = float(profil.daily_rate) / daily_budget
    if ratio <= 1:
        return WEIGHTS["budget"], "Tarif dans le budget"
    if ratio <= 1.2:
        return WEIGHTS["budget"] / 2, "Tarif légèrement au-dessus du budget"
    return 0, "Tarif au-dessus du budget"


def _availability(offer: Offer, profil: Profil, ctx: ProfilContext):
    max_points = WEIGHTS["availability"]
    period = offer_period(offer)
    if period is None:
        return (max_points, "Ouvert aux opportunités") if profil.is_open_to_work else (0, "Non disponible")
    start, end = period
    overlapping = [a for a in ctx.availabilities if a.start_date <= end and a.end_date >= start]
    if any(a.status in ("busy", "leave") for a in overlapping):
        return 0, "Occupé sur la période"
    if any(a.status == "partial" for a in overlapping):
        return 6, "Partiellement disponible"
    # Aucune période occupée sur ces dates : le membre est disponible (c'est l'état par défaut)
    return (max_points, "Disponible sur la période") if profil.is_open_to_work else (0, "Non disponible")


def _reputation(offer: Offer, profil: Profil, ctx: ProfilContext):
    if ctx.rating_avg is None:
        return WEIGHTS["reputation"] / 2, "Pas encore d'avis"
    return WEIGHTS["reputation"] * ctx.rating_avg / 5, f"Note moyenne {ctx.rating_avg:.1f} / 5"


_RULES = {
    "skills": _skills,
    "experience": _experience,
    "location": _location,
    "budget": _budget,
    "availability": _availability,
    "reputation": _reputation,
}


def compute_score(offer: Offer, profil: Profil, ctx: ProfilContext, required_ids: Optional[List[int]] = None) -> dict:
    """Score d'un profil pour une offre : total sur 100, détail par critère et compétences en commun.

    `required_ids` évite de relire les compétences requises quand l'appelant les a déjà chargées.
    """
    if required_ids is None:
        required_ids = [skill.id for skill in offer.required_skills.all()]
    breakdown = []
    for key, rule in _RULES.items():
        if key == "skills":
            score, detail = rule(offer, profil, ctx, required_ids)
        else:
            score, detail = rule(offer, profil, ctx)
        breakdown.append({"key": key, "label": LABELS[key], "score": round(score), "max": WEIGHTS[key], "detail": detail})
    return {
        "score": min(100, sum(item["score"] for item in breakdown)),
        "breakdown": breakdown,
        "matched_skill_ids": [skill_id for skill_id in required_ids if skill_id in ctx.skill_levels],
    }
