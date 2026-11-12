"""Service « mon espace marketplace » : le profil et l'entreprise de l'utilisateur connecté.

Ces opérations ne passent pas par les permissions RBAC `profils.*` / `companies.*` (réservées à l'administration) :
chaque utilisateur authentifié gère uniquement ses propres données.
"""
from typing import Any, Dict, Optional, Tuple

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.text import slugify

from app.marketplace.models import Company, Profil


class MeService:
    """Profil et entreprise de l'utilisateur connecté."""

    @staticmethod
    def get_profil(user) -> Optional[Profil]:
        """Profil de l'utilisateur, ou None s'il n'en a pas encore."""
        return Profil.objects.select_related("company").filter(user=user).first()

    @classmethod
    def get_space(cls, user) -> Tuple[Optional[Profil], Optional[Company]]:
        """Retourne (profil, entreprise) de l'utilisateur."""
        profil = cls.get_profil(user)
        return profil, (profil.company if profil else None)

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
        """Crée le profil de l'utilisateur (un compte, un profil)."""
        if Profil.objects.filter(user=user).exists():
            raise ValidationError("Vous avez déjà un profil marketplace.")
        full_name = f"{user.first_name} {user.last_name}".strip()
        slug = cls._unique_slug(Profil, full_name or user.email.split("@")[0], "profil")
        return Profil.objects.create(user=user, slug=slug, created_by=user.id, updated_by=user.id, **data)

    @staticmethod
    def update_profil(user, data: Dict[str, Any]) -> Optional[Profil]:
        """Met à jour le profil de l'utilisateur ; None s'il n'en a pas."""
        profil = Profil.objects.filter(user=user).first()
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
        """Crée l'entreprise de l'utilisateur et la rattache à son profil, dont il devient propriétaire."""
        profil = cls.get_profil(user)
        if profil is None:
            raise ValidationError("Créez d'abord votre profil.")
        if profil.company_id:
            raise ValidationError("Votre profil est déjà rattaché à une entreprise.")
        slug = cls._unique_slug(Company, data["name"], "entreprise")
        company = Company.objects.create(slug=slug, created_by=user.id, updated_by=user.id, **data)
        profil.company = company
        profil.is_company_owner = True
        profil.updated_by = user.id
        profil.save()
        return company

    @staticmethod
    def update_company(user, data: Dict[str, Any]) -> Optional[Company]:
        """Met à jour l'entreprise ; réservé au propriétaire. None si l'utilisateur n'a pas d'entreprise."""
        profil = Profil.objects.select_related("company").filter(user=user).first()
        if profil is None or profil.company is None:
            return None
        if not profil.is_company_owner:
            raise ValidationError("Seul le propriétaire peut modifier l'entreprise.")
        company = profil.company
        for field, value in data.items():
            setattr(company, field, value)
        company.updated_by = user.id
        company.save()
        return company
