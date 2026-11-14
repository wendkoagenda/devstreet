"""
Fabriques de données valides pour la marketplace (tests et seeds de démonstration).

Chaque fabrique crée aussi les objets liés requis (profil, entreprise, offre…) quand ils ne sont pas fournis,
pour respecter les clés étrangères non nulles et les contraintes d'unicité.
"""
import uuid
from datetime import date, datetime, timedelta, timezone as dt_timezone
from decimal import Decimal

from django.contrib.auth import get_user_model

from app.marketplace.models import (
    Availability,
    Candidature,
    Company,
    Connection,
    Experience,
    Offer,
    Prestation,
    Profil,
    ProfilHistory,
    ProfilSkill,
    Review,
    Skill,
    Swipe,
)


def _suffix() -> str:
    return uuid.uuid4().hex[:8]


def _audit(by) -> dict:
    """Champs système created_by / updated_by (entiers) à partir d'un utilisateur."""
    return {"created_by": by.id, "updated_by": by.id}


def make_user(**overrides):
    """Utilisateur ordinaire (compte d'un profil marketplace)."""
    User = get_user_model()
    suffix = _suffix()
    return User.objects.create_user(
        username=overrides.pop("username", f"mp_{suffix}"),
        email=overrides.pop("email", f"mp_{suffix}@example.com"),
        password=overrides.pop("password", None),
        **overrides,
    )


def make_company(by, **overrides):
    suffix = _suffix()
    data = {
        "name": f"Entreprise {suffix}",
        "slug": f"entreprise-{suffix}",
        "sector": "fintech",
        "country": "BF",
        "city": "Ouagadougou",
        **_audit(by),
    }
    data.update(overrides)
    return Company.objects.create(**data)


def make_skill(by, **overrides):
    suffix = _suffix()
    data = {"name": f"Competence {suffix}", "slug": f"competence-{suffix}", "type": "hard", "category": "backend", **_audit(by)}
    data.update(overrides)
    return Skill.objects.create(**data)


def make_profil(by, **overrides):
    """Profil dev par défaut ; avec `type="entreprise"`, une entreprise est créée si elle n'est pas fournie."""
    suffix = _suffix()
    if overrides.get("company") is not None:
        overrides.setdefault("type", "entreprise")  # un profil rattaché à une entreprise est un profil entreprise
    if overrides.get("type") == "entreprise" and not overrides.get("company"):
        overrides["company"] = make_company(by)
    data = {
        "user": overrides.pop("user", None) or make_user(),
        "slug": f"profil-{suffix}",
        "headline": "Développeur Django / React",
        "country": "BF",
        "city": "Ouagadougou",
        **_audit(by),
    }
    data.update(overrides)
    return Profil.objects.create(**data)


def make_offer(by, **overrides):
    suffix = _suffix()
    company = overrides.pop("company", None) or make_company(by)
    data = {
        "company": company,
        "recruiter": overrides.pop("recruiter", None) or make_profil(by, type="entreprise", company=company),
        "title": f"Développeur backend {suffix}",
        "slug": f"offre-{suffix}",
        "description": "Mission de développement d'une API Django REST.",
        "type": "mission",
        "experience_level": "mid",
        "country": "BF",
        **_audit(by),
    }
    data.update(overrides)
    return Offer.objects.create(**data)


def make_candidature(by, **overrides):
    data = {
        "offer": overrides.pop("offer", None) or make_offer(by),
        "profil": overrides.pop("profil", None) or make_profil(by),
        "message": "Je souhaite candidater à cette offre.",
        **_audit(by),
    }
    data.update(overrides)
    return Candidature.objects.create(**data)


def make_profil_skill(by, **overrides):
    data = {
        "profil": overrides.pop("profil", None) or make_profil(by),
        "skill": overrides.pop("skill", None) or make_skill(by),
        "level": 3,
        "years": 2,
        **_audit(by),
    }
    data.update(overrides)
    return ProfilSkill.objects.create(**data)


def make_experience(by, **overrides):
    data = {
        "profil": overrides.pop("profil", None) or make_profil(by),
        "title": "Développeur fullstack",
        "company_name": "Acme",
        "start_date": date(2024, 1, 1),
        **_audit(by),
    }
    data.update(overrides)
    return Experience.objects.create(**data)


def make_prestation(by, **overrides):
    suffix = _suffix()
    data = {
        "profil": overrides.pop("profil", None) or make_profil(by),
        "title": f"Landing page en 5 jours {suffix}",
        "slug": f"prestation-{suffix}",
        "description": "Création d'une landing page responsive.",
        "category": "web",
        "price": Decimal("150000.00"),
        "delivery_days": 5,
        **_audit(by),
    }
    data.update(overrides)
    return Prestation.objects.create(**data)


def make_profil_history(by, **overrides):
    data = {
        "profil": overrides.pop("profil", None) or make_profil(by),
        "field": "headline",
        "old_value": "Ancienne accroche",
        "new_value": "Nouvelle accroche",
        **_audit(by),
    }
    data.update(overrides)
    return ProfilHistory.objects.create(**data)


def make_availability(by, **overrides):
    data = {
        "profil": overrides.pop("profil", None) or make_profil(by),
        "start_date": date(2026, 1, 1),
        "end_date": date(2026, 1, 31),
        "status": "available",
        **_audit(by),
    }
    data.update(overrides)
    return Availability.objects.create(**data)


def make_review(by, **overrides):
    data = {
        "target": overrides.pop("target", None) or make_profil(by),
        "author": overrides.pop("author", None) or make_profil(by),
        "rating": 5,
        "comment": "Excellent travail.",
        **_audit(by),
    }
    data.update(overrides)
    return Review.objects.create(**data)


def make_swipe(by, **overrides):
    """Swipe de recrutement par défaut (profil entreprise vers profil dev) ; contexte réseau : dev vers dev."""
    author_type = "entreprise" if overrides.get("context", "recruit") == "recruit" else "dev"
    data = {
        "author": overrides.pop("author", None) or make_profil(by, type=author_type),
        "target": overrides.pop("target", None) or make_profil(by),
        "direction": "like",
        "context": "recruit",
        **_audit(by),
    }
    data.update(overrides)
    return Swipe.objects.create(**data)


def make_connection(by, **overrides):
    data = {
        "profil_a": overrides.pop("profil_a", None) or make_profil(by),
        "profil_b": overrides.pop("profil_b", None) or make_profil(by),
        "matched_at": datetime.now(dt_timezone.utc) - timedelta(days=1),
        **_audit(by),
    }
    data.update(overrides)
    return Connection.objects.create(**data)
