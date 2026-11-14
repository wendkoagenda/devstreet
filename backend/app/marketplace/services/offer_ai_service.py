"""
Génération d'offre marketplace par IA (UC-09).

L'entreprise décrit son besoin en langage naturel ; le LLM renvoie un JSON
validé, rattaché aux Skill existantes. L'humain reste maître : le formulaire
est prérempli, jamais publié automatiquement.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional

from django.core.cache import cache
from rest_framework.exceptions import ValidationError

from app.ai.errors import ExternalUnavailable, QuotaExceeded
from app.ai.providers.router import LlmRouter
from app.marketplace.models import Offer, Skill
from app.marketplace.services.market_service import MarketService

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Tu es l'assistant recrutement de DevStreet (marketplace tech Afrique de l'Ouest).
À partir du besoin d'une entreprise, tu rédiges une offre d'emploi / mission.
Réponds UNIQUEMENT avec un objet JSON valide (pas de markdown, pas de texte autour), schéma :

{
  "title": "string max 200",
  "description": "string, 2 à 4 paragraphes en français, clair et professionnel",
  "type": "mission|cdd|cdi|stage",
  "experience_level": "junior|mid|senior",
  "work_mode": "on_site|hybrid|remote",
  "contract_duration": null ou entier 1-36 (mois ; null pour CDI),
  "budget_min": null ou nombre,
  "budget_max": null ou nombre,
  "currency": "XOF",
  "budget_period": "day|month|fixed",
  "skills": ["nom de techno", "..."]  // 3 à 8 compétences concrètes
}

Règles : pas de critère discriminant (âge, sexe, nationalité). Budgets en XOF réalistes pour la région.
"""

OFFER_TYPES = {c[0] for c in Offer._meta.get_field("type").choices}
LEVELS = {c[0] for c in Offer._meta.get_field("experience_level").choices}
WORK_MODES = {c[0] for c in Offer._meta.get_field("work_mode").choices}
PERIODS = {c[0] for c in Offer._meta.get_field("budget_period").choices}

DAILY_QUOTA_KEY = "marketplace:offer_ai:{user_id}:{day}"
DAILY_QUOTA = 20


def _extract_json(raw: str) -> dict:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise ValidationError({"detail": "Réponse IA illisible (JSON attendu)."})
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise ValidationError({"detail": "Réponse IA illisible (JSON attendu)."}) from exc
    if not isinstance(data, dict):
        raise ValidationError({"detail": "Réponse IA invalide."})
    return data


_NUMBER = re.compile(r"[+-]?\d+(?:\.\d+)?")


def _number(value) -> Optional[float]:
    """Nombre lu dans une valeur de l'IA (nombre ou texte comme « 12 » / « 3500.5 ») ; None si absente ou illisible."""
    if isinstance(value, bool) or value is None:
        return None
    text = str(value).strip()
    return float(text) if _NUMBER.fullmatch(text) else None


def _match_skills(names: List[str]) -> List[dict]:
    """Rattache les noms renvoyés par l'IA aux Skill en base (création soft interdite)."""
    if not names:
        return []
    catalog = list(Skill.objects.all())
    by_lower = {skill.name.lower(): skill for skill in catalog}
    found: List[Skill] = []
    for raw in names[:12]:
        label = str(raw or "").strip()
        if not label:
            continue
        key = label.lower()
        skill = by_lower.get(key)
        if skill is None:
            # fuzzy : containment
            for candidate in catalog:
                cname = candidate.name.lower()
                if key in cname or cname in key:
                    skill = candidate
                    break
        if skill and skill not in found:
            found.append(skill)
    return [
        {"id": skill.id, "name": skill.name, "type": skill.type, "category": skill.category}
        for skill in found[:10]
    ]


def _normalize_draft(data: dict, *, country: str, city: str) -> Dict[str, Any]:
    title = str(data.get("title") or "").strip()[:200]
    description = str(data.get("description") or "").strip()
    if not title or not description:
        raise ValidationError({"detail": "L'IA n'a pas fourni titre et description."})

    offer_type = str(data.get("type") or "mission").lower()
    if offer_type not in OFFER_TYPES:
        offer_type = "mission"
    level = str(data.get("experience_level") or "mid").lower()
    if level not in LEVELS:
        level = "mid"
    work_mode = str(data.get("work_mode") or "hybrid").lower()
    if work_mode not in WORK_MODES:
        work_mode = "hybrid"
    period = str(data.get("budget_period") or "month").lower()
    if period not in PERIODS:
        period = "month"

    duration_number = _number(data.get("contract_duration"))
    duration = int(duration_number) if duration_number is not None else None
    if offer_type == "cdi":
        duration = None
    elif duration is not None:
        duration = max(1, min(36, duration))

    def _money(value) -> Optional[float]:
        number = _number(value)
        return round(number, 2) if number is not None else None

    skills_raw = data.get("skills") or []
    if not isinstance(skills_raw, list):
        skills_raw = []
    skills = _match_skills([str(s) for s in skills_raw])
    budget_min = _money(data.get("budget_min"))
    budget_max = _money(data.get("budget_max"))

    return {
        "title": title,
        "description": description,
        "type": offer_type,
        "experience_level": level,
        "work_mode": work_mode,
        "contract_duration": duration,
        "budget_min": budget_min,
        "budget_max": budget_max,
        "currency": str(data.get("currency") or "XOF").upper()[:3],
        "budget_period": period,
        "country": (country or "SN").upper()[:2],
        "city": (city or "")[:100],
        "required_skill_ids": [s["id"] for s in skills],
        "skills": skills,
    }


class OfferAiService:
    """Rédaction d'offre + suggestion de profils (déterministe) pour un recruteur."""

    def __init__(self, router: LlmRouter | None = None):
        self.router = router or LlmRouter()

    def _check_quota(self, user) -> None:
        from django.utils import timezone

        day = timezone.localdate().isoformat()
        key = DAILY_QUOTA_KEY.format(user_id=user.id, day=day)
        used = cache.get(key, 0)
        if used >= DAILY_QUOTA:
            raise QuotaExceeded("Quota quotidien de génération d'offres atteint.")
        cache.set(key, used + 1, timeout=60 * 60 * 26)

    def generate(self, user, brief: str) -> Dict[str, Any]:
        recruiter = MarketService._recruiter(user)
        text = (brief or "").strip()
        if len(text) < 12:
            raise ValidationError({"brief": "Décrivez le besoin en au moins une phrase."})
        if len(text) > 4000:
            raise ValidationError({"brief": "Texte trop long (max 4000 caractères)."})

        self._check_quota(user)

        company = recruiter.company
        context = (
            f"Entreprise : {company.name}. Secteur : {company.sector}. "
            f"Pays : {company.country}. Ville : {company.city or 'n/a'}."
        )
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"{context}\n\nBesoin de l'entreprise :\n{text}",
            },
        ]

        try:
            result = self.router.complete(messages, timeout=35.0)
        except ExternalUnavailable:
            raise
        except Exception as exc:
            logger.exception("Génération offre IA échouée")
            raise ExternalUnavailable("Service IA indisponible.") from exc

        raw = _extract_json(result.content)
        draft = _normalize_draft(
            raw,
            country=company.country,
            city=company.city or "",
        )

        # Suggestions déterministes à partir d'une offre éphémère (non persistée)
        suggested = self._suggest_profils(draft, company_id=company.id)

        return {
            "draft": draft,
            "suggested_profils": suggested,
            "provider": result.provider,
            "model": result.model,
        }

    def _suggest_profils(self, draft: Dict[str, Any], *, company_id: int) -> List[dict]:
        """Top profils via scoring déterministe sur une offre virtuelle."""
        from app.marketplace.models import Profil
        from app.marketplace.presenters import profil_card
        from app.marketplace.services.scoring import build_contexts, compute_score

        class _FakeOffer:
            pass

        fake = _FakeOffer()
        fake.type = draft["type"]
        fake.experience_level = draft["experience_level"]
        fake.work_mode = draft["work_mode"]
        fake.country = draft["country"]
        fake.city = draft["city"]
        fake.budget_min = draft["budget_min"]
        fake.budget_max = draft["budget_max"]
        fake.currency = draft["currency"]
        fake.budget_period = draft["budget_period"]
        fake.start_date = None
        fake.contract_duration = draft["contract_duration"]
        fake.deadline = None

        required = draft["required_skill_ids"]
        profils = list(
            Profil.objects.filter(is_open_to_work=True)
            .exclude(company_id=company_id)
            .select_related("user")
            .prefetch_related("profil_skills__skill")[:300]
        )
        contexts = build_contexts(profils)
        rows = []
        for profil in profils:
            ctx = contexts[profil.id]
            scoring = compute_score(fake, profil, ctx, required)
            card = profil_card(profil, ctx)
            card.update(score=scoring["score"], breakdown=scoring["breakdown"])
            rows.append(card)
        rows.sort(key=lambda item: -item["score"])
        return rows[:5]
