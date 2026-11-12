"""Représentations JSON « écran » des objets de la marketplace (listes, fiches, cartes).

Les vues utilisateur n'exposent que ce qui est nécessaire à l'écran : jamais le compte complet, ni les
champs système. Les appelants préchargent les relations (select_related / prefetch_related) pour les listes.
"""
from typing import Optional

from app.marketplace.models import Candidature, Offer, Profil


def _money(value) -> Optional[str]:
    return None if value is None else str(value)


def company_summary(company) -> dict:
    return {
        "id": company.id,
        "name": company.name,
        "slug": company.slug,
        "sector": company.sector,
        "city": company.city,
        "country": company.country,
        "is_verified": company.is_verified,
    }


def offer_dict(offer: Offer, scoring: Optional[dict] = None, candidature: Optional[Candidature] = None, detail: bool = False) -> dict:
    """Offre avec son entreprise et ses compétences requises ; `scoring` ajoute score et détail, `candidature` la mienne."""
    data = {
        "id": offer.id,
        "slug": offer.slug,
        "title": offer.title,
        "type": offer.type,
        "contract_duration": offer.contract_duration,
        "experience_level": offer.experience_level,
        "budget_min": _money(offer.budget_min),
        "budget_max": _money(offer.budget_max),
        "currency": offer.currency,
        "budget_period": offer.budget_period,
        "country": offer.country,
        "city": offer.city,
        "work_mode": offer.work_mode,
        "start_date": offer.start_date.isoformat() if offer.start_date else None,
        "deadline": offer.deadline.isoformat() if offer.deadline else None,
        "status": offer.status,
        "published_at": offer.published_at.isoformat() if offer.published_at else None,
        "company": company_summary(offer.company),
        "skills": [{"id": skill.id, "name": skill.name} for skill in offer.required_skills.all()],
    }
    if detail:
        data["description"] = offer.description
        data["views_count"] = offer.views_count
    if scoring is not None:
        data["score"] = scoring["score"]
        data["breakdown"] = scoring["breakdown"]
        data["matched_skill_ids"] = scoring["matched_skill_ids"]
    if candidature is not None:
        data["my_candidature"] = {
            "id": candidature.id,
            "status": candidature.status,
            "created_at": candidature.created_at.isoformat(),
        }
    return data


def profil_name(profil: Profil) -> str:
    user = profil.user
    return user.full_name or user.email.split("@")[0]


def profil_card(profil: Profil, context=None, with_email: bool = False) -> dict:
    """Carte d'un profil (liste de talents, candidatures reçues) ; l'e-mail n'est exposé que si l'appelant y a droit."""
    levels = sorted(profil.profil_skills.all(), key=lambda item: -item.level)
    data = {
        "id": profil.id,
        "name": profil_name(profil),
        "headline": profil.headline,
        "city": profil.city,
        "country": profil.country,
        "remote": profil.remote,
        "years_of_experience": profil.years_of_experience,
        "is_open_to_work": profil.is_open_to_work,
        "skills": [item.skill.name for item in levels[:6]],
        "rating_avg": round(context.rating_avg, 1) if context and context.rating_avg is not None else None,
        "reviews_count": context.reviews_count if context else 0,
    }
    if with_email:
        data["email"] = profil.user.email
    return data


def candidature_dict(candidature: Candidature, with_offer: bool = False) -> dict:
    data = {
        "id": candidature.id,
        "status": candidature.status,
        "message": candidature.message,
        "created_at": candidature.created_at.isoformat(),
        "decided_at": candidature.decided_at.isoformat() if candidature.decided_at else None,
    }
    if with_offer:
        data["offer"] = offer_dict(candidature.offer)
    return data
