"""Service « réseau » : découverte de profils par swipe, vivier du recruteur, connexions et fiche publique.

Deux contextes de swipe (modèle Swipe.context) :
- `recruit` : un recruteur parcourt des talents ; un like les place dans le vivier de son entreprise ;
- `network` : un dev parcourt d'autres devs ; un like réciproque crée une Connection (« amis »).

UC-08 : annuaire filtrable (`search_talents`) pour contacter sans publier d'offre.
"""
from datetime import date
from typing import List, Optional

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from app.marketplace.models import Availability, Candidature, Connection, Offer, Profil, Review, Swipe
from app.marketplace.presenters import profil_card
from app.marketplace.services.cv_service import can_download_cv
from app.marketplace.services.me_service import MeService
from app.marketplace.services.scoring import build_contexts, compute_score

DECK_SIZE = 20
DIRECTORY_SIZE = 100
CONTEXTS = ("recruit", "network")


ACTING_AS = ("dev", "entreprise")


def _card_queryset(all_types: bool = False):
    """
    Cartes de découverte. Le recrutement ne propose que des profils dev ; le réseau (général) propose
    aussi des profils entreprise.
    """
    queryset = Profil.objects.select_related("user", "company").prefetch_related("profil_skills__skill")
    return queryset if all_types else queryset.filter(type=Profil.TYPE_DEV)


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

    @staticmethod
    def _viewer(user) -> Profil:
        """Profil du lecteur d'une fiche : son profil dev, sinon son profil entreprise (recruteur sans profil dev)."""
        profil = MeService.get_profil(user) or MeService.get_entreprise_profil(user)
        if profil is None:
            raise PermissionDenied("Créez d'abord votre profil marketplace.")
        return profil

    @classmethod
    def _profil_for_context(cls, user, context: str, acting: Optional[str] = None) -> Profil:
        """
        Profil avec lequel le membre agit. Recrutement : son profil entreprise. Réseau : le profil choisi par
        `acting` (dev ou entreprise), sinon son profil dev, sinon son profil entreprise.
        """
        if context not in CONTEXTS:
            raise ValidationError({"context": "Contexte invalide (recruit ou network)."})
        if context == "recruit":
            # Le recrutement se fait avec le profil entreprise, jamais avec le profil dev
            profil = MeService.get_entreprise_profil(user)
            if profil is None:
                raise PermissionDenied("Réservé aux recruteurs : créez d'abord votre entreprise.")
            return profil
        if acting is not None and acting not in ACTING_AS:
            raise ValidationError({"acting": "Valeur invalide (dev ou entreprise)."})
        if acting == "entreprise":
            profil = MeService.get_entreprise_profil(user)
        elif acting == "dev":
            profil = MeService.get_profil(user)
        else:
            profil = MeService.get_profil(user) or MeService.get_entreprise_profil(user)
        if profil is None:
            raise PermissionDenied("Créez d'abord votre profil marketplace.")
        return profil

    # ── Paquet de cartes ─────────────────────────────────────────────────────

    @classmethod
    def deck(cls, user, context: str, acting: Optional[str] = None) -> List[dict]:
        """Profils à découvrir (non encore swipés dans ce contexte), les plus pertinents d'abord."""
        me = cls._profil_for_context(user, context, acting)
        swiped = Swipe.objects.filter(author=me, context=context).values_list("target_id", flat=True)
        # Jamais ses propres profils (dev et entreprise)
        candidates = (
            _card_queryset(all_types=context == "network").exclude(user_id=me.user_id).exclude(id__in=swiped)
        )
        if context == "recruit":
            colleagues = Profil.objects.filter(company_id=me.company_id).values("user_id")
            candidates = candidates.filter(is_open_to_work=True).exclude(user_id__in=colleagues)
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

    # ── Annuaire (UC-08) ─────────────────────────────────────────────────────

    @classmethod
    def search_talents(cls, user, filters: Optional[dict] = None) -> List[dict]:
        """Annuaire recruteur : filtres compétence, pays, disponibilité, remote, recherche texte."""
        me = cls._profil_for_context(user, "recruit")
        filters = filters or {}
        today = timezone.localdate()

        candidates = (
            _card_queryset()
            .filter(is_open_to_work=True)
            .exclude(id=me.id)
            .exclude(company_id=me.company_id)
        )

        search = (filters.get("search") or "").strip()
        if search:
            candidates = candidates.filter(
                Q(headline__icontains=search)
                | Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(profil_skills__skill__name__icontains=search)
            ).distinct()

        country = (filters.get("country") or "").strip().upper()
        if country:
            candidates = candidates.filter(country=country)

        if (filters.get("remote") or "").lower() in ("1", "true", "yes"):
            candidates = candidates.filter(remote=True)

        skill = (filters.get("skill") or "").strip()
        if skill:
            if skill.isdigit():
                candidates = candidates.filter(profil_skills__skill_id=int(skill)).distinct()
            else:
                candidates = candidates.filter(profil_skills__skill__name__icontains=skill).distinct()

        if (filters.get("available") or "").lower() in ("1", "true", "yes"):
            available_ids = (
                Availability.objects.filter(
                    status__in=("available", "partial"),
                    end_date__gte=today,
                )
                .values_list("profil_id", flat=True)
                .distinct()
            )
            candidates = candidates.filter(id__in=available_ids)

        profils = list(candidates.order_by("-years_of_experience", "id")[:DIRECTORY_SIZE])
        contexts = build_contexts(profils)
        availability = _next_available([p.id for p in profils], today)
        rows = []
        for profil in profils:
            card = profil_card(profil, contexts[profil.id])
            card["available_from"] = availability[profil.id].isoformat() if profil.id in availability else None
            rows.append(card)
        return rows

    # ── Swipe ────────────────────────────────────────────────────────────────

    @classmethod
    @transaction.atomic
    def swipe(cls, user, target_id: int, direction: str, context: str, acting: Optional[str] = None) -> dict:
        """Enregistre un like ou un passe. Un like réseau réciproque crée la connexion."""
        me = cls._profil_for_context(user, context, acting)
        target = _card_queryset(all_types=context == "network").filter(id=target_id).first()
        if target is None or target.user_id == me.user_id:
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
    def undo_last_swipe(cls, user, context: str, acting: Optional[str] = None) -> dict:
        """Annule le dernier choix du contexte ; retire la connexion qu'il avait créée."""
        me = cls._profil_for_context(user, context, acting)
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
        """Mes connexions (like mutuel), avec mon profil dev comme avec mon profil entreprise, et les coordonnées de contact."""
        mine = list(Profil.objects.filter(user=user).values_list("id", flat=True))
        if not mine:
            raise PermissionDenied("Créez d'abord votre profil marketplace.")
        rows = (
            Connection.objects.filter(Q(profil_a_id__in=mine) | Q(profil_b_id__in=mine), status="matched")
            .select_related("profil_a__user", "profil_a__company", "profil_b__user", "profil_b__company")
            .order_by("-matched_at")
        )
        others = [(row, row.profil_b if row.profil_a_id in mine else row.profil_a) for row in rows]
        contexts = build_contexts([other for _row, other in others])
        result = []
        for row, other in others:
            card = profil_card(other, contexts[other.id], with_email=True)
            card["matched_at"] = row.matched_at.isoformat()
            result.append(card)
        return result

    @classmethod
    def requests(cls, user) -> dict:
        """
        Demandes de connexion du réseau, avec mon profil dev comme avec mon profil entreprise :
        - `sent` : celles que j'ai envoyées et qui attendent une réponse ;
        - `received` : celles des profils qui ont proposé de se connecter et à qui je n'ai pas encore répondu.
        Chaque ligne est la carte de l'autre profil, avec la date de la demande et `acting` : celui de mes profils
        concerné (« dev » ou « entreprise »), à utiliser pour répondre.
        """
        mine = {row["id"]: row["type"] for row in Profil.objects.filter(user=user).values("id", "type")}
        if not mine:
            raise PermissionDenied("Créez d'abord votre profil marketplace.")
        connected = set()
        for a_id, b_id in Connection.objects.filter(
            Q(profil_a_id__in=mine) | Q(profil_b_id__in=mine), status="matched"
        ).values_list("profil_a_id", "profil_b_id"):
            connected.add(b_id if a_id in mine else a_id)
        network = Swipe.objects.filter(context="network", direction="like")
        answered = set(Swipe.objects.filter(context="network", author_id__in=mine).values_list("target_id", flat=True))

        def build(rows, other_field: str, mine_field: str, exclude: set) -> List[dict]:
            seen, result = set(), []
            for swipe in rows:
                other = getattr(swipe, other_field)
                if other.id in seen or other.id in exclude:
                    continue
                seen.add(other.id)
                card = profil_card(other)
                card["requested_at"] = swipe.created_at.isoformat()
                card["acting"] = mine[getattr(swipe, f"{mine_field}_id")]
                result.append(card)
            return result

        sent = (
            network.filter(author_id__in=mine)
            .select_related("target__user", "target__company")
            .prefetch_related("target__profil_skills__skill")
            .order_by("-created_at")
        )
        received = (
            network.filter(target_id__in=mine)
            .select_related("author__user", "author__company")
            .prefetch_related("author__profil_skills__skill")
            .order_by("-created_at")
        )
        return {
            "sent": build(sent, "target", "author", connected),
            "received": build(received, "author", "target", connected | answered),
        }

    # ── Fiche publique ───────────────────────────────────────────────────────

    @classmethod
    def can_see_email(cls, viewer: Profil, target: Profil) -> bool:
        """Coordonnées visibles : soi-même, une connexion, un candidat à une offre de mon entreprise ou un membre de mon vivier."""
        if viewer.id == target.id:
            return True
        low, high = sorted((viewer.id, target.id))
        if Connection.objects.filter(profil_a_id=low, profil_b_id=high, status="matched").exists():
            return True
        company_id = MeService.company_id_of(viewer.user_id)
        if company_id is None:
            return False
        applied = Candidature.objects.filter(profil=target, offer__company_id=company_id).exists()
        pooled = target.is_open_to_work and Swipe.objects.filter(
            author__company_id=company_id, target=target, context="recruit", direction="like"
        ).exists()
        return applied or pooled

    @classmethod
    def _can_view(cls, viewer: Profil, target: Profil) -> bool:
        """Un profil est visible s'il est ouvert aux opportunités, ou si le lien avec le lecteur le justifie."""
        return target.is_open_to_work or cls.can_see_email(viewer, target)

    @classmethod
    def public_profile(cls, user, profil_id: int) -> dict:
        viewer = cls._viewer(user)
        target = _card_queryset().filter(id=profil_id).first()
        if target is None or not cls._can_view(viewer, target):
            raise NotFound("Profil introuvable.")
        ctx = build_contexts([target])[target.id]
        data = profil_card(target, ctx, with_email=cls.can_see_email(viewer, target))
        data.update(
            {
                "is_self": viewer.id == target.id,
                "username": target.user.username,
                "bio": target.bio,
                "languages": [item.get("language") for item in target.languages if isinstance(item, dict)],
                "github_url": target.github_url,
                "linkedin_url": target.linkedin_url,
                "portfolio_url": target.portfolio_url,
                "cv_visibility": target.cv_visibility,
                "can_download_cv": can_download_cv(viewer, target),
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
                "prestations": [
                    {
                        "id": row.id,
                        "title": row.title,
                        "slug": row.slug,
                        "description": row.description,
                        "category": row.category,
                        "price": str(row.price),
                        "currency": row.currency,
                        "delivery_days": row.delivery_days,
                        "revisions": row.revisions,
                    }
                    for row in target.prestations.filter(is_active=True).order_by("-created_at")
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
