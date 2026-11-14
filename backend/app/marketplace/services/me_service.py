"""Service « mon espace marketplace » : les profils et l'entreprise de l'utilisateur connecté.

Un membre peut avoir un profil `dev` et un profil `entreprise` (au plus un de chaque type). Le profil `entreprise`
est toujours rattaché à une entreprise ; le profil `dev` porte compétences, expériences, candidatures, etc.

Ces opérations ne passent pas par les permissions RBAC `profils.*` / `companies.*` (réservées à l'administration) :
chaque utilisateur authentifié gère uniquement ses propres données.
"""
from typing import Any, Dict, Optional, Tuple

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.text import slugify

from app.marketplace.models import Company, Profil


class MeService:
    """Profils et entreprise de l'utilisateur connecté."""

    @staticmethod
    def get_profil(user) -> Optional[Profil]:
        """Profil dev de l'utilisateur, ou None s'il n'en a pas encore."""
        return Profil.objects.filter(user=user, type=Profil.TYPE_DEV).first()

    @staticmethod
    def get_entreprise_profil(user) -> Optional[Profil]:
        """Profil entreprise de l'utilisateur (avec son entreprise), ou None."""
        return Profil.objects.select_related("company").filter(user=user, type=Profil.TYPE_ENTREPRISE).first()

    @staticmethod
    def company_id_of(user_id: int) -> Optional[int]:
        """Identifiant de l'entreprise du membre (via son profil entreprise), ou None."""
        return (
            Profil.objects.filter(user_id=user_id, type=Profil.TYPE_ENTREPRISE)
            .values_list("company_id", flat=True)
            .first()
        )

    @classmethod
    def get_space(cls, user) -> Tuple[Optional[Profil], Optional[Company]]:
        """Retourne (profil dev, entreprise) de l'utilisateur."""
        entreprise = cls.get_entreprise_profil(user)
        return cls.get_profil(user), (entreprise.company if entreprise else None)

    @staticmethod
    def _unique_slug(model, base: str, fallback: str) -> str:
        """Slug unique dérivé de `base` : suffixe numérique en cas de collision."""
        root = (slugify(base) or fallback)[:150]
        slug, index = root, 2
        while model.objects.filter(slug=slug).exists():
            slug = f"{root}-{index}"
            index += 1
        return slug

    @classmethod
    @transaction.atomic
    def create_profil(cls, user, data: Dict[str, Any]) -> Profil:
        """Crée le profil dev de l'utilisateur (un profil dev par compte)."""
        if cls.get_profil(user) is not None:
            raise ValidationError("Vous avez déjà un profil marketplace.")
        full_name = f"{user.first_name} {user.last_name}".strip()
        slug = cls._unique_slug(Profil, full_name or user.email.split("@")[0], "profil")
        return Profil.objects.create(
            user=user, type=Profil.TYPE_DEV, slug=slug, created_by=user.id, updated_by=user.id, **data
        )

    @classmethod
    def update_profil(cls, user, data: Dict[str, Any]) -> Optional[Profil]:
        """Met à jour le profil dev de l'utilisateur ; None s'il n'en a pas."""
        profil = cls.get_profil(user)
        if profil is None:
            return None
        for field, value in data.items():
            setattr(profil, field, value)
        profil.updated_by = user.id
        profil.save()
        return profil

    @classmethod
    @transaction.atomic
    def create_company(cls, user, data: Dict[str, Any]) -> Company:
        """Crée l'entreprise de l'utilisateur et son profil entreprise, dont il devient propriétaire."""
        # Le profil dev n'est pas nécessaire : un membre peut n'avoir qu'un profil entreprise
        if cls.get_entreprise_profil(user) is not None:
            raise ValidationError("Vous êtes déjà rattaché à une entreprise.")
        slug = cls._unique_slug(Company, data["name"], "entreprise")
        company = Company.objects.create(slug=slug, created_by=user.id, updated_by=user.id, **data)
        cls.create_entreprise_profil(user, company, is_owner=True)
        return company

    @classmethod
    def create_entreprise_profil(cls, user, company: Company, is_owner: bool) -> Profil:
        """Crée le profil entreprise d'un membre pour l'entreprise donnée (un seul par membre)."""
        full_name = f"{user.first_name} {user.last_name}".strip() or user.email.split("@")[0]
        slug = cls._unique_slug(Profil, f"{full_name}-{company.name}", "profil-entreprise")
        return Profil.objects.create(
            user=user,
            type=Profil.TYPE_ENTREPRISE,
            company=company,
            is_company_owner=is_owner,
            slug=slug,
            country=company.country,
            city=company.city,
            created_by=user.id,
            updated_by=user.id,
        )

    @classmethod
    def update_company(cls, user, data: Dict[str, Any]) -> Optional[Company]:
        """Met à jour l'entreprise ; réservé au propriétaire. None si l'utilisateur n'a pas d'entreprise."""
        profil = cls.get_entreprise_profil(user)
        if profil is None:
            return None
        if not profil.is_company_owner:
            raise ValidationError("Seul le propriétaire peut modifier l'entreprise.")
        company = profil.company
        for field, value in data.items():
            setattr(company, field, value)
        company.updated_by = user.id
        company.save()
        return company
