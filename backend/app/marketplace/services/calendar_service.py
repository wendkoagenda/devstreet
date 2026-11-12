"""Service « mon calendrier » et « mes expériences » : périodes de disponibilité et parcours du profil connecté."""
from typing import Any, Dict, List

from django.db import transaction
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from app.marketplace.models import Availability, Experience, Profil
from app.marketplace.services.me_service import MeService


def _profil(user) -> Profil:
    profil = MeService.get_profil(user)
    if profil is None:
        raise PermissionDenied("Créez d'abord votre profil marketplace.")
    return profil


def availability_dict(row: Availability) -> dict:
    return {
        "id": row.id,
        "start_date": row.start_date.isoformat(),
        "end_date": row.end_date.isoformat(),
        "status": row.status,
        "hours_per_week": row.hours_per_week,
        "source": row.source,
        "note": row.note,
    }


def experience_dict(row: Experience) -> dict:
    return {
        "id": row.id,
        "title": row.title,
        "company_name": row.company_name,
        "location": row.location,
        "contract_type": row.contract_type,
        "start_date": row.start_date.isoformat(),
        "end_date": row.end_date.isoformat() if row.end_date else None,
        "is_current": row.is_current,
        "description": row.description,
        "technologies": row.technologies,
    }


class CalendarService:
    """Périodes du calendrier de disponibilité (saisie manuelle ; les missions acceptées sont ajoutées automatiquement)."""

    @staticmethod
    def list_mine(user) -> List[dict]:
        profil = _profil(user)
        return [availability_dict(row) for row in Availability.objects.filter(profil=profil).order_by("start_date", "id")]

    @staticmethod
    def _check_no_overlap(profil: Profil, start, end, exclude_id=None) -> None:
        overlapping = Availability.objects.filter(profil=profil, start_date__lte=end, end_date__gte=start)
        if exclude_id:
            overlapping = overlapping.exclude(id=exclude_id)
        if overlapping.exists():
            raise ValidationError({"error": "Cette période chevauche une période déjà enregistrée."})

    @classmethod
    @transaction.atomic
    def create(cls, user, data: Dict[str, Any]) -> dict:
        profil = _profil(user)
        cls._check_no_overlap(profil, data["start_date"], data["end_date"])
        row = Availability.objects.create(
            profil=profil, source="manual", created_by=user.id, updated_by=user.id, **data
        )
        return availability_dict(row)

    @classmethod
    def _own_manual(cls, user, availability_id: int) -> Availability:
        profil = _profil(user)
        row = Availability.objects.filter(id=availability_id, profil=profil).first()
        if row is None:
            raise NotFound("Période introuvable.")
        if row.source == "mission":
            raise ValidationError({"error": "Une période créée par une mission n'est pas modifiable."})
        return row

    @classmethod
    @transaction.atomic
    def update(cls, user, availability_id: int, data: Dict[str, Any]) -> dict:
        row = cls._own_manual(user, availability_id)
        start = data.get("start_date", row.start_date)
        end = data.get("end_date", row.end_date)
        if end < start:
            raise ValidationError({"end_date": "La fin doit suivre le début."})
        cls._check_no_overlap(row.profil, start, end, exclude_id=row.id)
        for field, value in data.items():
            setattr(row, field, value)
        row.updated_by = user.id
        row.save()
        return availability_dict(row)

    @classmethod
    def delete(cls, user, availability_id: int) -> None:
        cls._own_manual(user, availability_id).delete()


class ExperienceService:
    """Expériences professionnelles du profil connecté."""

    @staticmethod
    def list_mine(user) -> List[dict]:
        profil = _profil(user)
        return [experience_dict(row) for row in Experience.objects.filter(profil=profil).order_by("-start_date", "-id")]

    @staticmethod
    def _normalize(data: Dict[str, Any]) -> Dict[str, Any]:
        """Une expérience en cours n'a pas de date de fin."""
        if data.get("is_current"):
            data["end_date"] = None
        return data

    @classmethod
    def create(cls, user, data: Dict[str, Any]) -> dict:
        profil = _profil(user)
        row = Experience.objects.create(
            profil=profil, created_by=user.id, updated_by=user.id, **cls._normalize(dict(data))
        )
        return experience_dict(row)

    @staticmethod
    def _own(user, experience_id: int) -> Experience:
        profil = _profil(user)
        row = Experience.objects.filter(id=experience_id, profil=profil).first()
        if row is None:
            raise NotFound("Expérience introuvable.")
        return row

    @classmethod
    def update(cls, user, experience_id: int, data: Dict[str, Any]) -> dict:
        row = cls._own(user, experience_id)
        data = cls._normalize(dict(data))
        start = data.get("start_date", row.start_date)
        end = data.get("end_date", row.end_date)
        if end is not None and end < start:
            raise ValidationError({"end_date": "La fin doit suivre le début."})
        for field, value in data.items():
            setattr(row, field, value)
        row.updated_by = user.id
        row.save()
        return experience_dict(row)

    @classmethod
    def delete(cls, user, experience_id: int) -> None:
        cls._own(user, experience_id).delete()

