"""Profils marketplace d'un membre, exposés sur sa page de profil (/profil/<nom>).

Un membre peut avoir un profil `dev` et un profil `entreprise`. Cette vue ne contient que ce que la page de profil
affiche : un résumé du profil dev (le détail passe par la fiche publique existante) et la fiche de l'entreprise avec
ses offres. Les deux profils restent étanches : les offres ne figurent jamais côté dev, ni les compétences côté entreprise.
"""
from typing import Optional

from app.marketplace.models import Offer, Profil
from app.marketplace.services.me_service import MeService
from app.marketplace.services.stats_service import connections_count


def _dev_summary(profil: Optional[Profil]) -> Optional[dict]:
    if profil is None:
        return None
    return {
        "id": profil.id,
        "headline": profil.headline,
        "city": profil.city,
        "country": profil.country,
        "is_open_to_work": profil.is_open_to_work,
    }


def _offer_row(offer: Offer) -> dict:
    return {
        "id": offer.id,
        "title": offer.title,
        "type": offer.type,
        "work_mode": offer.work_mode,
        "city": offer.city,
        "country": offer.country,
        "status": offer.status,
        "published_at": offer.published_at.isoformat() if offer.published_at else None,
    }


def _entreprise_summary(profil: Optional[Profil], viewer, is_self: bool) -> Optional[dict]:
    if profil is None:
        return None
    company = profil.company
    # Coordonnées sensibles : seulement pour les membres de la même entreprise
    is_member = is_self or MeService.company_id_of(viewer.id) == company.id
    # Les offres de l'entreprise (comme « Mes offres »), quel que soit leur auteur dans l'équipe :
    # les membres de l'entreprise voient aussi brouillons et offres clôturées, les autres seulement les offres ouvertes.
    offers = Offer.objects.filter(company_id=company.id)
    if not is_member:
        offers = offers.filter(status="open")
    data = {
        "id": profil.id,
        "is_owner": profil.is_company_owner,
        "is_member": is_member,
        "company": {
            "id": company.id,
            "name": company.name,
            "slug": company.slug,
            "description": company.description,
            "sector": company.sector,
            "size": company.size,
            "website": company.website,
            "country": company.country,
            "city": company.city,
            "is_verified": company.is_verified,
        },
        "offers": [_offer_row(offer) for offer in offers.order_by("-published_at", "-id")[:50]],
    }
    if is_member:
        data["company"].update(contact_email=company.contact_email, phone=company.phone, address=company.address)
    return data


def member_profiles_payload(viewer, user) -> dict:
    """Résumés des profils dev et entreprise du membre `user`, vus par `viewer`."""
    is_self = viewer.id == user.id
    return {
        # Visible sur la page de profil : connexions du membre, avec son profil dev comme avec son profil entreprise
        "connections_count": connections_count(user),
        "profil_dev": _dev_summary(MeService.get_profil(user)),
        "profil_entreprise": _entreprise_summary(MeService.get_entreprise_profil(user), viewer, is_self),
    }
