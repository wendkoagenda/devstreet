"""
E-mails de la marketplace : candidature déposée, décision, mise en relation, invitation d'entreprise.

Chaque fonction extrait des modèles les valeurs simples attendues par le catalogue (`core.services.email_catalog`)
et programme l'envoi après la validation de la transaction : un échec d'envoi n'annule jamais l'action.
"""
from django.core.cache import cache

from app.core.services import email_catalog
from app.core.services.email_service import EmailService
from app.marketplace.models import Candidature, Profil

MESSAGE_EXCERPT_LENGTH = 280
# Délai pendant lequel une même mise en relation (annulée puis refaite) n'est pas renotifiée
MATCH_EMAIL_COOLDOWN_SECONDS = 60 * 60


def _first_name(user) -> str:
    return user.first_name or user.username


def _display_name(user) -> str:
    return user.full_name or user.username


def _excerpt(text: str) -> str:
    text = ' '.join((text or '').split())
    if len(text) <= MESSAGE_EXCERPT_LENGTH:
        return text
    return text[: MESSAGE_EXCERPT_LENGTH - 1].rstrip() + '…'


def company_member_users(company_id: int):
    """Membres de l'entreprise (propriétaire et membres invités) actifs, un par compte."""
    seen = set()
    rows = (
        Profil.objects.filter(type=Profil.TYPE_ENTREPRISE, company_id=company_id, user__is_active=True)
        .select_related('user')
        .order_by('-is_company_owner', 'id')
    )
    for profil in rows:
        if profil.user_id not in seen:
            seen.add(profil.user_id)
            yield profil.user


def notify_application(candidature: Candidature) -> None:
    """Accusé au candidat et « nouvelle candidature » à chaque membre de l'entreprise (e-mails séparés)."""
    service = EmailService()
    offer = candidature.offer
    candidate = candidature.profil.user
    service.queue(
        email_catalog.application_sent(candidate.email, _first_name(candidate), offer.title, offer.company.name)
    )
    for member in company_member_users(offer.company_id):
        if member.id == candidate.id:
            continue
        service.queue(
            email_catalog.application_received(
                member.email,
                _first_name(member),
                _display_name(candidate),
                candidature.profil.headline,
                offer.title,
                offer.id,
                _excerpt(candidature.message),
            )
        )


def notify_decision(candidature: Candidature, previous_status: str) -> None:
    """E-mail au candidat quand la candidature passe à « acceptée » ou « refusée » (jamais deux fois)."""
    status = candidature.status
    if status == previous_status or status not in ('accepted', 'rejected'):
        return
    offer = candidature.offer
    candidate = candidature.profil.user
    build = email_catalog.application_accepted if status == 'accepted' else email_catalog.application_rejected
    EmailService().queue(build(candidate.email, _first_name(candidate), offer.title, offer.company.name))


def notify_match(profil_a: Profil, profil_b: Profil) -> None:
    """Prévient les deux membres d'une nouvelle mise en relation (une fois par heure et par paire)."""
    low, high = sorted((profil_a.id, profil_b.id))
    # cache.add n'écrit que si la clé est absente : une mise en relation refaite dans l'heure n'est pas renotifiée
    if not cache.add(f'marketplace:match-email:{low}:{high}', True, MATCH_EMAIL_COOLDOWN_SECONDS):
        return
    service = EmailService()
    for me, other in ((profil_a, profil_b), (profil_b, profil_a)):
        service.queue(
            email_catalog.network_match(
                me.user.email,
                _first_name(me.user),
                _display_name(other.user),
                other.headline,
                other.id,
            )
        )


def notify_company_invitation(to_email: str, inviter, company_name: str, link: str, validity_days: int) -> None:
    """Invitation à rejoindre une entreprise."""
    EmailService().queue(
        email_catalog.company_invitation(
            to_email, inviter.full_name or inviter.email, company_name, link, validity_days
        )
    )
