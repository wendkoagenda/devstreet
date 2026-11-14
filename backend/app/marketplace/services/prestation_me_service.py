"""Prestations packagées du profil connecté (UC-14)."""
from typing import Any, Dict, List

from rest_framework.exceptions import NotFound, PermissionDenied

from app.marketplace.models import Prestation, Profil
from app.marketplace.services.me_service import MeService


def _profil(user) -> Profil:
    profil = MeService.get_profil(user)
    if profil is None:
        raise PermissionDenied("Créez d'abord votre profil marketplace.")
    return profil


def prestation_dict(row: Prestation) -> dict:
    return {
        "id": row.id,
        "title": row.title,
        "slug": row.slug,
        "description": row.description,
        "category": row.category,
        "price": str(row.price),
        "currency": row.currency,
        "delivery_days": row.delivery_days,
        "revisions": row.revisions,
        "cover_image": row.cover_image,
        "is_active": row.is_active,
    }


class PrestationMeService:
    """CRUD des services packagés du talent connecté."""

    @staticmethod
    def list_mine(user) -> List[dict]:
        profil = _profil(user)
        rows = Prestation.objects.filter(profil=profil).order_by("-created_at", "-id")
        return [prestation_dict(row) for row in rows]

    @staticmethod
    def list_active_for(profil: Profil) -> List[dict]:
        rows = Prestation.objects.filter(profil=profil, is_active=True).order_by("-created_at", "-id")
        return [prestation_dict(row) for row in rows]

    @classmethod
    def create(cls, user, data: Dict[str, Any]) -> dict:
        profil = _profil(user)
        payload = dict(data)
        payload.pop("slug", None)
        slug = MeService._unique_slug(Prestation, payload["title"], "prestation")
        row = Prestation.objects.create(
            profil=profil,
            slug=slug,
            created_by=user.id,
            updated_by=user.id,
            **payload,
        )
        return prestation_dict(row)

    @staticmethod
    def _own(user, prestation_id: int) -> Prestation:
        profil = _profil(user)
        row = Prestation.objects.filter(id=prestation_id, profil=profil).first()
        if row is None:
            raise NotFound("Prestation introuvable.")
        return row

    @classmethod
    def update(cls, user, prestation_id: int, data: Dict[str, Any]) -> dict:
        row = cls._own(user, prestation_id)
        payload = dict(data)
        payload.pop("slug", None)
        for field, value in payload.items():
            setattr(row, field, value)
        row.updated_by = user.id
        row.save()
        return prestation_dict(row)

    @classmethod
    def delete(cls, user, prestation_id: int) -> None:
        cls._own(user, prestation_id).delete()
