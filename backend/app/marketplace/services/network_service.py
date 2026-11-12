"""Service « réseau » : découverte de profils par swipe, vivier du recruteur, connexions et fiche publique.

Deux contextes de swipe (modèle Swipe.context) :
- `recruit` : un recruteur parcourt des talents ; un like les place dans le vivier de son entreprise ;
- `network` : un dev parcourt d'autres devs ; un like réciproque crée une Connection (« amis »).
"""
from datetime import date
from typing import List, Optional

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from app.marketplace.models import Availability, Candidature, Connection, Offer, Profil, Review, Swipe
from app.marketplace.presenters import profil_card
from app.marketplace.services.me_service import MeService
from app.marketplace.services.scoring import build_contexts, compute_score

DECK_SIZE = 20
CONTEXTS = ("recruit", "network")


def _card_queryset():
    return Profil.objects.select_related("user").prefetch_related("profil_skills__skill")


def _next_available(profil_ids, today: date) -> dict:
    """Prochaine date de disponibilité par profil (période « disponible » ou « partiel » commençant aujourd'hui ou plus tard)."""
    result = {}
    rows = (
        Availability.objects.filter(profil_id__in=profil_ids, status__in=("available", "partial"), end_date__gte=today)
        .order_by("start_date")
        .values("profil_id", "start_date")
    )
    for row in rows:
        result.setdefault(row["profil_id"], max(row["start_date"], today))
    return result


class NetworkService:
    """Opérations de découverte et de mise en relation."""

    # ── Accès ────────────────────────────────────────────────────────────────

    @staticmethod
    def _profil(user) -> Profil:
        profil = MeService.get_profil(user)
        if profil is None:
            raise PermissionDenied("Créez d'abord votre profil marketplace.")
        return profil

    @classmethod
    def _profil_for_context(cls, user, context: str) -> Profil:
        if context not in CONTEXTS:
            raise ValidationError({"context": "Contexte invalide (recruit ou network)."})
        profil = cls._profil(user)
        if context == "recruit" and profil.company_id is None:
            raise PermissionDenied("Réservé aux recruteurs : créez d'abord votre entreprise.")
        return profil

    # ── Paquet de cartes ─────────────────────────────────────────────────────

    @classmethod
    def deck(cls, user, context: str) -> List[dict]:
        """Profils à découvrir (non encore swipés dans ce contexte), les plus pertinents d'abord."""
        me = cls._profil_for_context(user, context)
        swiped = Swipe.objects.filter(author=me, context=context).values_list("target_id", flat=True)
        candidates = _card_queryset().exclude(id=me.id).exclude(id__in=swiped)
        if context == "recruit":
            candidates = candidates.filter(is_open_to_work=True).exclude(company_id=me.company_id)
        else:
            blocked = Connection.objects.filter(Q(profil_a=me) | Q(profil_b=me), status="blocked")
            hidden = {c.profil_a_id for c in blocked} | {c.profil_b_id for c in blocked}
            candidates = candidates.exclude(id__in=hidden)
        profils = list(candidates[:300])
        contexts = build_contexts(profils)
        availability = _next_available([p.id for p in profils], timezone.localdate())
        my_skill_ids = set(me.profil_skills.values_list("skill_id", flat=True))
        offers = (
            list(Offer.objects.filter(company_id=me.company_id, status="open").prefetch_related("required_skills"))
            if context == "recruit"
            else []
        )
        rows = []
        for profil in profils:
            ctx = contexts[profil.id]
            card = profil_card(profil, ctx)
            card["available_from"] = availability[profil.id].isoformat() if profil.id in availability else None
            if context == "recruit":
                # meilleur score parmi les offres ouvertes de l'entreprise ; sans offre, pas de score
                card["score"] = max((compute_score(offer, profil, ctx)["score"] for offer in offers), default=None)
            else:
                common = [item.skill.name for item in profil.profil_skills.all() if item.skill_id in my_skill_ids]
                card["common_skills"] = common
                card["score"] = None
            rows.append(card)
        rows.sort(
            key=lambda row: (
                -(row["score"] if row["score"] is not None else 0),
                -len(row.get("common_skills", [])),
                -(row["rating_avg"] or 0),
                -row["years_of_experience"],
            )
        )
        return rows[:DECK_SIZE]

    # ── Swipe ────────────────────────────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def swipe(cls, user, target_id: int, direction: str, context: str) -> dict:
        """Enregistre un like ou un passe. Un like réseau réciproque crée la connexion."""
        me = cls._profil_for_context(user, context)
        target = _card_queryset().filter(id=target_id).first()
        if target is None or target.id == me.id:
            raise NotFound("Profil introuvable.")
        if Swipe.objects.filter(author=me, target=target, context=context).exists():
            raise ValidationError({"error": "Vous avez déjà choisi pour ce profil."})
        Swipe.objects.create(
            author=me, target=target, direction=direction, context=context, created_by=user.id, updated_by=user.id
        )
        matched = False
        if context == "network" and direction == "like":
            mutual = Swipe.objects.filter(author=target, target=me, context="network", direction="like").exists()
            if mutual:
                low, high = sorted((me.id, target.id))
                Connection.objects.get_or_create(
                    profil_a_id=low,
                    profil_b_id=high,
                    defaults={"status": "matched", "matched_at": timezone.now(), "created_by": user.id, "updated_by": user.id},
                )
                matched = True
        return {"matched": matched, "profil": profil_card(target)}

    @classmethod
    @transaction.atomic
    def undo_last_swipe(cls, user, context: str) -> dict:
        """Annule le dernier choix du contexte ; retire la connexion qu'il avait créée."""
        me = cls._profil_for_context(user, context)
        last = Swipe.objects.filter(author=me, context=context).order_by("-created_at", "-id").first()
        if last is None:
            raise NotFound("Aucun choix à annuler.")
        target_id = last.target_id
        if context == "network" and last.direction == "like":
            low, high = sorted((me.id, target_id))
            Connection.objects.filter(profil_a_id=low, profil_b_id=high, status="matched").delete()
        last.delete()
        return {"undone": target_id}

    # ── Vivier et connexions ─────────────────────────────────────────────────

    @classmethod
    def pool(cls, user) -> List[dict]:
        """Vivier de l'entreprise : profils likés en contexte recruit par ses recruteurs (le plus récent d'abord)."""
        me = cls._profil_for_context(user, "recruit")
        likes = list(
            Swipe.objects.filter(author__company_id=me.company_id, context="recruit", direction="like")
            .select_related("target__user", "author__user")
            .prefetch_related("target__profil_skills__skill")
            .order_by("-created_at")
        )
        seen, rows = set(), []
        contexts = build_contexts([like.target for like in likes])
        for like in likes:
            if like.target_id in seen:
                continue
            seen.add(like.target_id)
            card = profil_card(like.target, contexts[like.target_id], with_email=like.target.is_open_to_work)
            card["liked_at"] = like.created_at.isoformat()
            card["liked_by"] = like.author.user.full_name or like.author.user.email
            rows.append(card)
        return rows

    @classmethod
    def connections(cls, user) -> List[dict]:
        """Mes connexions (like mutuel) avec les coordonnées de contact."""
        me = cls._profil(user)
        rows = (
            Connection.objects.filter(Q(profil_a=me) | Q(profil_b=me), status="matched")
            .select_related("profil_a__user", "profil_b__user")
            .order_by("-matched_at")
        )
        others = [(row, row.profil_b if row.profil_a_id == me.id else row.profil_a) for row in rows]
        contexts = build_contexts([other for _row, other in others])
        result = []
        for row, other in others:
            card = profil_card(other, contexts[other.id], with_email=True)
            card["matched_at"] = row.matched_at.isoformat()
            result.append(card)
        return result

    # ── Fiche publique ───────────────────────────────────────────────────────

    @classmethod
    def can_see_email(cls, viewer: Profil, target: Profil) -> bool:
        """Coordonnées visibles : soi-même, une connexion, un candidat à une offre de mon entreprise ou un membre de mon vivier."""
        if viewer.id == target.id:
            return True
        low, high = sorted((viewer.id, target.id))
        if Connection.objects.filter(profil_a_id=low, profil_b_id=high, status="matched").exists():
            return True
        if viewer.company_id is None:
            return False
        applied = Candidature.objects.filter(profil=target, offer__company_id=viewer.company_id).exists()
        pooled = target.is_open_to_work and Swipe.objects.filter(
            author__company_id=viewer.company_id, target=target, context="recruit", direction="like"
        ).exists()
        return applied or pooled

    @classmethod
    def _can_view(cls, viewer: Profil, target: Profil) -> bool:
        """Un profil est visible s'il est ouvert aux opportunités, ou si le lien avec le lecteur le justifie."""
        return target.is_open_to_work or cls.can_see_email(viewer, target)

    @classmethod
    def public_profile(cls, user, profil_id: int) -> dict:
        viewer = cls._profil(user)
        target = _card_queryset().filter(id=profil_id).first()
        if target is None or not cls._can_view(viewer, target):
            raise NotFound("Profil introuvable.")
        ctx = build_contexts([target])[target.id]
        data = profil_card(target, ctx, with_email=cls.can_see_email(viewer, target))
        data.update(
            {
                "is_self": viewer.id == target.id,
                "bio": target.bio,
                "languages": [item.get("language") for item in target.languages if isinstance(item, dict)],
                "github_url": target.github_url,
                "linkedin_url": target.linkedin_url,
                "portfolio_url": target.portfolio_url,
                "cv_visibility": target.cv_visibility,
                "member_since": target.created_at.date().isoformat(),
                "skills_detail": [
                    {"name": item.skill.name, "level": item.level, "years": item.years}
                    for item in sorted(target.profil_skills.all(), key=lambda row: -row.level)
                ],
                "experiences": [
                    {
                        "id": exp.id,
                        "title": exp.title,
                        "company_name": exp.company_name,
                        "location": exp.location,
                        "start_date": exp.start_date.isoformat(),
                        "end_date": exp.end_date.isoformat() if exp.end_date else None,
                        "is_current": exp.is_current,
                        "description": exp.description,
                        "technologies": exp.technologies,
                    }
                    for exp in target.experiences.order_by("-start_date")
                ],
                "reviews": [
                    {
                        "rating": review.rating,
                        "comment": review.comment,
                        "author": review.author.user.full_name or "Anonyme",
                        "created_at": review.created_at.date().isoformat(),
                    }
                    for review in Review.objects.filter(target=target, is_public=True)
                    .select_related("author__user")
                    .order_by("-created_at")[:10]
                ],
            }
        )
        return data
