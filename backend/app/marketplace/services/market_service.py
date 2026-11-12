"""Service « marché » : offres, candidatures et compétences côté utilisateur (candidat ou recruteur).

Comme `MeService`, il ne passe pas par les permissions RBAC d'administration : chaque règle d'accès est portée
ici (un candidat voit les offres ouvertes ; un recruteur ne gère que les offres de son entreprise).
"""
import logging
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Count, F, Q
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from app.marketplace.models import Availability, Candidature, Offer, Profil, ProfilSkill, Skill
from app.marketplace.presenters import candidature_dict, offer_dict, profil_card
from app.marketplace.services.me_service import MeService
from app.marketplace.services.scoring import build_contexts, compute_score, mission_period, offer_period

logger = logging.getLogger(__name__)

LIST_LIMIT = 50
DECISIONS = ("shortlisted", "rejected", "accepted")


def _offer_queryset():
    return Offer.objects.select_related("company").prefetch_related("required_skills")


class MarketService:
    """Opérations sur les offres, candidatures et compétences."""

    # ── Accès ────────────────────────────────────────────────────────────────

    @staticmethod
    def _profil(user) -> Profil:
        profil = MeService.get_profil(user)
        if profil is None:
            raise PermissionDenied("Créez d'abord votre profil marketplace.")
        return profil

    @classmethod
    def _recruiter(cls, user) -> Profil:
        profil = cls._profil(user)
        if profil.company_id is None:
            raise PermissionDenied("Réservé aux recruteurs : créez d'abord votre entreprise.")
        return profil

    @classmethod
    def _company_offer(cls, user, offer_id: int) -> Offer:
        """Offre de l'entreprise du recruteur (404 sinon, pour ne pas révéler l'existence d'offres d'autres entreprises)."""
        profil = cls._recruiter(user)
        offer = _offer_queryset().filter(id=offer_id, company_id=profil.company_id).first()
        if offer is None:
            raise NotFound("Offre introuvable.")
        return offer

    # ── Compétences ──────────────────────────────────────────────────────────

    @staticmethod
    def list_skills(search: Optional[str] = None) -> List[dict]:
        queryset = Skill.objects.order_by("name")
        if search:
            queryset = queryset.filter(name__icontains=search)
        return [
            {"id": skill.id, "name": skill.name, "type": skill.type, "category": skill.category}
            for skill in queryset[:200]
        ]

    @classmethod
    def get_my_skills(cls, user) -> List[dict]:
        profil = cls._profil(user)
        rows = ProfilSkill.objects.filter(profil=profil).select_related("skill").order_by("-level", "skill__name")
        return [
            {"skill_id": row.skill_id, "name": row.skill.name, "type": row.skill.type, "level": row.level, "years": row.years}
            for row in rows
        ]

    @classmethod
    @transaction.atomic
    def set_my_skills(cls, user, items: List[dict]) -> List[dict]:
        """Remplace les compétences du profil par la liste fournie."""
        profil = cls._profil(user)
        wanted = {item["skill_id"]: item for item in items}
        existing = set(Skill.objects.filter(id__in=wanted).values_list("id", flat=True))
        unknown = set(wanted) - existing
        if unknown:
            raise ValidationError({"skills": f"Compétence(s) inconnue(s) : {sorted(unknown)}"})
        ProfilSkill.objects.filter(profil=profil).exclude(skill_id__in=wanted).delete()
        for skill_id, item in wanted.items():
            ProfilSkill.objects.update_or_create(
                profil=profil,
                skill_id=skill_id,
                defaults={
                    "level": item["level"],
                    "years": item.get("years", 0),
                    "created_by": user.id,
                    "updated_by": user.id,
                },
            )
        return cls.get_my_skills(user)

    # ── Offres (candidat) ────────────────────────────────────────────────────

    @classmethod
    def list_open_offers(cls, user, search: Optional[str] = None, offer_type: Optional[str] = None, work_mode: Optional[str] = None) -> List[dict]:
        """Offres ouvertes (hors entreprise du recruteur), triées par score si l'utilisateur a un profil."""
        profil = MeService.get_profil(user)
        queryset = _offer_queryset().filter(status="open")
        if profil and profil.company_id:
            queryset = queryset.exclude(company_id=profil.company_id)
        if offer_type:
            queryset = queryset.filter(type=offer_type)
        if work_mode:
            queryset = queryset.filter(work_mode=work_mode)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(company__name__icontains=search)
                | Q(required_skills__name__icontains=search)
            ).distinct()
        offers = list(queryset.order_by("-published_at", "-id")[:LIST_LIMIT])
        return cls._scored_offers(profil, offers)

    @classmethod
    def _scored_offers(cls, profil: Optional[Profil], offers: List[Offer]) -> List[dict]:
        if profil is None:
            return [offer_dict(offer) for offer in offers]
        context = build_contexts([profil])[profil.id]
        mine = {c.offer_id: c for c in Candidature.objects.filter(profil=profil, offer__in=offers)}
        rows = [offer_dict(offer, compute_score(offer, profil, context), mine.get(offer.id)) for offer in offers]
        return sorted(rows, key=lambda row: -row["score"])

    @classmethod
    def get_offer(cls, user, offer_id: int) -> dict:
        """Fiche d'une offre : ouverte pour tous, brouillon ou clôturée pour l'entreprise seulement."""
        profil = MeService.get_profil(user)
        offer = _offer_queryset().filter(id=offer_id).first()
        if offer is None:
            raise NotFound("Offre introuvable.")
        is_own = bool(profil and profil.company_id == offer.company_id)
        if offer.status != "open" and not is_own:
            raise NotFound("Offre introuvable.")
        if offer.status == "open" and not is_own:
            Offer.objects.filter(id=offer.id).update(views_count=F("views_count") + 1)
            offer.views_count += 1
        scoring = candidature = None
        if profil:
            scoring = compute_score(offer, profil, build_contexts([profil])[profil.id])
            candidature = Candidature.objects.filter(offer=offer, profil=profil).first()
        data = offer_dict(offer, scoring, candidature, detail=True)
        data["is_own"] = is_own
        return data

    @classmethod
    @transaction.atomic
    def apply(cls, user, offer_id: int, message: str) -> dict:
        profil = cls._profil(user)
        offer = _offer_queryset().filter(id=offer_id, status="open").first()
        if offer is None:
            raise NotFound("Offre introuvable ou fermée.")
        if offer.company_id == profil.company_id:
            raise ValidationError({"error": "Vous ne pouvez pas postuler à l'offre de votre propre entreprise."})
        if Candidature.objects.filter(offer=offer, profil=profil).exists():
            raise ValidationError({"error": "Vous avez déjà postulé à cette offre."})
        candidature = Candidature.objects.create(
            offer=offer, profil=profil, message=message, status="sent", created_by=user.id, updated_by=user.id
        )
        return candidature_dict(candidature)

    @classmethod
    def my_candidatures(cls, user) -> List[dict]:
        profil = cls._profil(user)
        rows = (
            Candidature.objects.filter(profil=profil)
            .select_related("offer__company")
            .prefetch_related("offer__required_skills")
            .order_by("-created_at")
        )
        return [candidature_dict(row, with_offer=True) for row in rows]

    # ── Offres (recruteur) ───────────────────────────────────────────────────

    @classmethod
    def my_offers(cls, user) -> List[dict]:
        profil = cls._recruiter(user)
        offers = (
            _offer_queryset()
            .filter(company_id=profil.company_id)
            .annotate(
                candidatures_total=Count("candidatures", distinct=True),
                candidatures_new=Count("candidatures", filter=Q(candidatures__status="sent"), distinct=True),
            )
            .order_by("-created_at")
        )
        rows = []
        for offer in offers:
            row = offer_dict(offer)
            row["candidatures_count"] = offer.candidatures_total
            row["candidatures_new"] = offer.candidatures_new
            rows.append(row)
        return rows

    @classmethod
    @transaction.atomic
    def create_offer(cls, user, data: Dict[str, Any]) -> dict:
        profil = cls._recruiter(user)
        skill_ids = data.pop("required_skill_ids", [])
        publish = data.pop("publish", False)
        data.pop("status", None)
        slug = MeService._unique_slug(Offer, data["title"], "offre")
        offer = Offer.objects.create(
            company_id=profil.company_id,
            recruiter=profil,
            slug=slug,
            status="open" if publish else "draft",
            published_at=timezone.now() if publish else None,
            created_by=user.id,
            updated_by=user.id,
            **data,
        )
        offer.required_skills.set(skill_ids)
        return offer_dict(_offer_queryset().get(id=offer.id), detail=True)

    @classmethod
    @transaction.atomic
    def update_offer(cls, user, offer_id: int, data: Dict[str, Any]) -> dict:
        offer = cls._company_offer(user, offer_id)
        skill_ids = data.pop("required_skill_ids", None)
        data.pop("publish", None)
        status = data.pop("status", None)
        for field, value in data.items():
            setattr(offer, field, value)
        if status and status != offer.status:
            offer.status = status
            if status == "open" and offer.published_at is None:
                offer.published_at = timezone.now()
        offer.updated_by = user.id
        offer.save()
        if skill_ids is not None:
            offer.required_skills.set(skill_ids)
        return offer_dict(_offer_queryset().get(id=offer.id), detail=True)

    @classmethod
    def get_my_offer(cls, user, offer_id: int) -> dict:
        return offer_dict(cls._company_offer(user, offer_id), detail=True)

    @classmethod
    def offer_candidatures(cls, user, offer_id: int) -> List[dict]:
        """Candidatures reçues, triées par score ; l'e-mail du candidat est exposé (il a postulé)."""
        offer = cls._company_offer(user, offer_id)
        rows = list(
            Candidature.objects.filter(offer=offer)
            .select_related("profil__user")
            .prefetch_related("profil__profil_skills__skill")
        )
        contexts = build_contexts([row.profil for row in rows])
        required = [skill.id for skill in offer.required_skills.all()]
        result = []
        for row in rows:
            ctx = contexts[row.profil_id]
            data = candidature_dict(row)
            data["score"] = compute_score(offer, row.profil, ctx, required)["score"]
            data["profil"] = profil_card(row.profil, ctx, with_email=True)
            result.append(data)
        return sorted(result, key=lambda item: -item["score"])

    @classmethod
    def recommended_profils(cls, user, offer_id: int, limit: int = 20) -> List[dict]:
        """Profils ouverts aux opportunités classés par score pour l'offre (hors profils de l'entreprise)."""
        offer = cls._company_offer(user, offer_id)
        profils = list(
            Profil.objects.filter(is_open_to_work=True)
            .exclude(company_id=offer.company_id)
            .select_related("user")
            .prefetch_related("profil_skills__skill")[:500]
        )
        contexts = build_contexts(profils)
        required = [skill.id for skill in offer.required_skills.all()]
        applied = set(Candidature.objects.filter(offer=offer).values_list("profil_id", flat=True))
        rows = []
        for profil in profils:
            ctx = contexts[profil.id]
            scoring = compute_score(offer, profil, ctx, required)
            card = profil_card(profil, ctx)
            card.update(score=scoring["score"], breakdown=scoring["breakdown"], applied=profil.id in applied)
            rows.append(card)
        return sorted(rows, key=lambda item: -item["score"])[:limit]

    # ── Décision ─────────────────────────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def decide(cls, user, candidature_id: int, status: str) -> dict:
        """Présélectionne, refuse ou accepte une candidature reçue. Accepter crée une période « occupé » au calendrier."""
        if status not in DECISIONS:
            raise ValidationError({"status": f"Décision invalide : {status}."})
        recruiter = cls._recruiter(user)
        candidature = (
            Candidature.objects.select_related("offer__company", "profil__user")
            .filter(id=candidature_id, offer__company_id=recruiter.company_id)
            .first()
        )
        if candidature is None:
            raise NotFound("Candidature introuvable.")
        if candidature.status == "accepted":
            raise ValidationError({"error": "Cette candidature est déjà acceptée."})
        candidature.status = status
        candidature.decided_at = timezone.now()
        candidature.updated_by = user.id
        candidature.save()
        if status == "accepted":
            cls._book_mission(candidature, user)
            cls._notify_accepted(candidature)
        return candidature_dict(candidature)

    @staticmethod
    def _book_mission(candidature: Candidature, user) -> None:
        """Ajoute la mission au calendrier du candidat (période « occupé », origine « mission »)."""
        offer = candidature.offer
        period = offer_period(offer) or mission_period(timezone.localdate(), offer.contract_duration, offer.type)
        Availability.objects.create(
            profil=candidature.profil,
            start_date=period[0],
            end_date=period[1],
            status="busy",
            source="mission",
            note=f"Mission : {offer.title}"[:255],
            created_by=user.id,
            updated_by=user.id,
        )

    @staticmethod
    def _notify_accepted(candidature: Candidature) -> None:
        """E-mail d'acceptation ; un échec d'envoi ne doit pas annuler la décision."""
        offer = candidature.offer
        try:
            send_mail(
                subject=f"Votre candidature a été acceptée : {offer.title}",
                message=(
                    f"Bonjour {candidature.profil.user.first_name},\n\n"
                    f"{offer.company.name} a accepté votre candidature pour « {offer.title} ». "
                    "La période de mission a été ajoutée à votre calendrier de disponibilité.\n\n"
                    "L'équipe DevStreet"
                ),
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                recipient_list=[candidature.profil.user.email],
                fail_silently=False,
            )
        except Exception:  # noqa: BLE001 - l'envoi d'e-mail ne doit jamais bloquer la décision
            logger.exception("Échec de l'envoi de l'e-mail d'acceptation (candidature %s)", candidature.id)
