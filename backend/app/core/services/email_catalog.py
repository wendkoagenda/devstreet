"""
Catalogue des e-mails transactionnels de DevStreet.

Chaque fonction construit un `EmailSpec` à partir de valeurs simples (jamais d'objet ORM) : les mêmes
fonctions servent aux actions réelles et à la commande d'aperçu (`preview_emails`). Les gabarits vivent
dans `core/templates/core/emails/` et héritent tous de `base.html` / `base.txt`.
"""
from datetime import datetime
from typing import Optional

from django.utils import formats, timezone, translation

from app.core.services.email_service import EmailSpec, frontend_link

ONBOARDING_PATH = '/onboarding'
ACCOUNT_RECOVERY_PATH = '/forgot-password'
LOGIN_PATH = '/login'
MY_APPLICATIONS_PATH = '/marketplace/applications'
OFFERS_PATH = '/marketplace/offers'


def _when(moment: Optional[datetime]) -> str:
    """Date et heure lisibles en français avec le fuseau, ex. « 15 novembre 2026 à 10:42 (UTC) »."""
    moment = timezone.localtime(moment or timezone.now())
    with translation.override('fr'):
        day = formats.date_format(moment, 'j F Y')
    return f"{day} à {moment:%H:%M} ({moment.tzname()})"


# ── Compte ──────────────────────────────────────────────────────────────────

def welcome(to_email: str, first_name: str) -> EmailSpec:
    """Bienvenue après la création du compte (inscription ou Google/GitHub)."""
    return EmailSpec(
        to_email=to_email,
        subject="Bienvenue sur DevStreet",
        template_name='welcome',
        context={
            'first_name': first_name,
            'preheader': "Votre compte est prêt : choisissez votre profil en deux minutes.",
            'cta_url': frontend_link(ONBOARDING_PATH),
            'cta_label': "Configurer mon espace",
        },
    )


def password_reset_code(to_email: str, first_name: str, code: str, ttl_minutes: int) -> EmailSpec:
    """Code du « mot de passe oublié »."""
    return EmailSpec(
        to_email=to_email,
        subject="Votre code de réinitialisation de mot de passe",
        template_name='password_reset',
        context={
            'first_name': first_name,
            'reset_code': code,
            'code_ttl_minutes': ttl_minutes,
            'login_url': frontend_link(LOGIN_PATH),
            'preheader': f"Votre code est valable {ttl_minutes} minutes.",
        },
    )


def password_change_code(to_email: str, first_name: str, code: str, ttl_minutes: int) -> EmailSpec:
    """Code de confirmation du changement de mot de passe (membre connecté)."""
    return EmailSpec(
        to_email=to_email,
        subject="Confirmez le changement de votre mot de passe",
        template_name='password_change_code',
        context={
            'first_name': first_name,
            'code': code,
            'code_ttl_minutes': ttl_minutes,
            'preheader': f"Votre code de confirmation est valable {ttl_minutes} minutes.",
        },
    )


def password_changed(to_email: str, first_name: str, changed_at: Optional[datetime] = None) -> EmailSpec:
    """Alerte de sécurité : le mot de passe vient d'être modifié."""
    return EmailSpec(
        to_email=to_email,
        subject="Votre mot de passe a été modifié",
        template_name='password_changed',
        context={
            'first_name': first_name,
            'changed_at': _when(changed_at),
            'preheader': "Si vous n'êtes pas à l'origine de ce changement, réagissez maintenant.",
            'cta_url': frontend_link(ACCOUNT_RECOVERY_PATH),
            'cta_label': "Ce n'était pas moi",
        },
    )


# ── Marketplace ─────────────────────────────────────────────────────────────

def application_sent(to_email: str, first_name: str, offer_title: str, company_name: str) -> EmailSpec:
    """Accusé de réception au candidat."""
    return EmailSpec(
        to_email=to_email,
        subject=f"Candidature envoyée : {offer_title}",
        template_name='application_sent',
        context={
            'first_name': first_name,
            'offer_title': offer_title,
            'company_name': company_name,
            'preheader': f"{company_name} a bien reçu votre candidature.",
            'cta_url': frontend_link(MY_APPLICATIONS_PATH),
            'cta_label': "Suivre mes candidatures",
        },
    )


def application_received(
    to_email: str,
    first_name: str,
    candidate_name: str,
    candidate_headline: str,
    offer_title: str,
    offer_id: int,
    message_excerpt: str = '',
) -> EmailSpec:
    """Nouvelle candidature, envoyée à chaque membre de l'entreprise."""
    return EmailSpec(
        to_email=to_email,
        subject=f"Nouvelle candidature : {offer_title}",
        template_name='application_received',
        context={
            'first_name': first_name,
            'candidate_name': candidate_name,
            'candidate_headline': candidate_headline,
            'offer_title': offer_title,
            'message_excerpt': message_excerpt,
            'preheader': f"{candidate_name} a postulé à « {offer_title} ».",
            'cta_url': frontend_link(f'/marketplace/my-offers/{offer_id}'),
            'cta_label': "Voir la candidature",
        },
    )


def application_accepted(to_email: str, first_name: str, offer_title: str, company_name: str) -> EmailSpec:
    """Candidature acceptée (la mission est ajoutée au calendrier du candidat)."""
    return EmailSpec(
        to_email=to_email,
        subject=f"Votre candidature a été acceptée : {offer_title}",
        template_name='application_accepted',
        context={
            'first_name': first_name,
            'offer_title': offer_title,
            'company_name': company_name,
            'preheader': f"Bonne nouvelle : {company_name} a accepté votre candidature.",
            'cta_url': frontend_link(MY_APPLICATIONS_PATH),
            'cta_label': "Voir ma candidature",
        },
    )


def application_rejected(to_email: str, first_name: str, offer_title: str, company_name: str) -> EmailSpec:
    """Candidature non retenue."""
    return EmailSpec(
        to_email=to_email,
        subject=f"Votre candidature : {offer_title}",
        template_name='application_rejected',
        context={
            'first_name': first_name,
            'offer_title': offer_title,
            'company_name': company_name,
            'preheader': f"Réponse de {company_name} à votre candidature.",
            'cta_url': frontend_link(OFFERS_PATH),
            'cta_label': "Découvrir d'autres offres",
        },
    )


def network_match(to_email: str, first_name: str, other_name: str, other_headline: str, other_profil_id: int) -> EmailSpec:
    """Mise en relation réciproque dans le Réseau."""
    return EmailSpec(
        to_email=to_email,
        subject=f"Vous êtes en relation avec {other_name}",
        template_name='network_match',
        context={
            'first_name': first_name,
            'other_name': other_name,
            'other_headline': other_headline,
            'preheader': f"{other_name} et vous vous êtes choisis mutuellement.",
            'cta_url': frontend_link(f'/marketplace/profiles/{other_profil_id}'),
            'cta_label': f"Voir le profil de {other_name}",
        },
    )


def company_invitation(
    to_email: str, inviter_name: str, company_name: str, link: str, validity_days: int
) -> EmailSpec:
    """Invitation à rejoindre une entreprise (le lien complet n'existe qu'au moment de la création)."""
    return EmailSpec(
        to_email=to_email,
        subject=f"Invitation à rejoindre {company_name} sur DevStreet",
        template_name='company_invitation',
        context={
            'inviter_name': inviter_name,
            'company_name': company_name,
            'validity_days': validity_days,
            'preheader': f"{inviter_name} vous invite à rejoindre {company_name}.",
            'cta_url': link,
            'cta_label': "Rejoindre l'entreprise",
        },
    )
