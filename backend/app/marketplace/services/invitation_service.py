"""Service « invitations d'entreprise » : le propriétaire invite, la personne invitée rejoint.

Règles : une invitation est à usage unique, révocable et expire ; un membre n'a qu'une entreprise ;
seul le propriétaire invite ou révoque. Seul le hash du jeton est conservé en base.
"""
import hashlib
import secrets
from datetime import timedelta
from typing import List, Optional

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from app.marketplace.services import marketplace_emails
from app.marketplace.models import InvitationEntreprise, Profil
from app.marketplace.services.me_service import MeService


VALIDITY_DAYS = 7
LIST_LIMIT = 50

# États présentés à l'utilisateur
STATE_VALID = "valid"
STATE_EXPIRED = "expired"
STATE_REVOKED = "revoked"
STATE_ACCEPTED = "accepted"

STATE_MESSAGES = {
    STATE_EXPIRED: "Cette invitation a expiré. Demandez-en une nouvelle au propriétaire de l'entreprise.",
    STATE_REVOKED: "Cette invitation a été révoquée par le propriétaire de l'entreprise.",
    STATE_ACCEPTED: "Cette invitation a déjà été utilisée.",
}


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def invitation_state(invitation: InvitationEntreprise) -> str:
    """État affiché : une invitation en attente dont la date est dépassée est « expirée »."""
    if invitation.status == InvitationEntreprise.STATUS_ACCEPTED:
        return STATE_ACCEPTED
    if invitation.status == InvitationEntreprise.STATUS_REVOKED:
        return STATE_REVOKED
    if invitation.expires_at <= timezone.now():
        return STATE_EXPIRED
    return STATE_VALID


def _row(invitation: InvitationEntreprise) -> dict:
    return {
        "id": invitation.id,
        "email": invitation.email,
        "state": invitation_state(invitation),
        "expires_at": invitation.expires_at.isoformat(),
        "created_at": invitation.created_at.isoformat(),
    }


class InvitationService:
    """Invitations à rejoindre une entreprise."""

    @staticmethod
    def invitation_path(token: str) -> str:
        return f"/entreprise/invitation/{token}"

    # ── Côté propriétaire ────────────────────────────────────────────────────

    @staticmethod
    def _owner_profil(user) -> Profil:
        profil = MeService.get_entreprise_profil(user)
        if profil is None or not profil.is_company_owner:
            raise PermissionDenied("Seul le propriétaire de l'entreprise peut gérer les invitations.")
        return profil

    @classmethod
    def list_for_owner(cls, user) -> List[dict]:
        profil = cls._owner_profil(user)
        rows = InvitationEntreprise.objects.filter(company_id=profil.company_id)[:LIST_LIMIT]
        return [_row(row) for row in rows]

    @classmethod
    @transaction.atomic
    def create(cls, user, email: str = "") -> dict:
        """Crée une invitation ; le lien complet n'est retourné qu'ici (et envoyé par e-mail si une adresse est donnée)."""
        profil = cls._owner_profil(user)
        token = secrets.token_urlsafe(32)
        invitation = InvitationEntreprise.objects.create(
            company=profil.company,
            invited_by=user,
            email=(email or "").strip().lower(),
            token_hash=_hash(token),
            expires_at=timezone.now() + timedelta(days=VALIDITY_DAYS),
        )
        link = f"{settings.FRONTEND_URL}{cls.invitation_path(token)}"
        if invitation.email:
            cls._send_email(invitation, user, link)
        data = _row(invitation)
        data["link"] = link
        return data

    @classmethod
    @transaction.atomic
    def revoke(cls, user, invitation_id: int) -> dict:
        profil = cls._owner_profil(user)
        invitation = (
            InvitationEntreprise.objects.select_for_update()
            .filter(id=invitation_id, company_id=profil.company_id)
            .first()
        )
        if invitation is None:
            raise NotFound("Invitation introuvable.")
        if invitation.status != InvitationEntreprise.STATUS_PENDING:
            raise ValidationError({"error": "Seule une invitation en attente peut être révoquée."})
        invitation.status = InvitationEntreprise.STATUS_REVOKED
        invitation.save(update_fields=["status", "updated_at"])
        return _row(invitation)

    @staticmethod
    def _send_email(invitation: InvitationEntreprise, inviter, link: str) -> None:
        """Envoi en arrière-plan : un échec ne doit pas annuler l'invitation, le propriétaire garde le lien à partager."""
        marketplace_emails.notify_company_invitation(
            invitation.email, inviter, invitation.company.name, link, VALIDITY_DAYS
        )

    # ── Côté personne invitée ────────────────────────────────────────────────

    @staticmethod
    def _by_token(token: str, for_update: bool = False) -> Optional[InvitationEntreprise]:
        queryset = InvitationEntreprise.objects.select_related("company")
        if for_update:
            queryset = queryset.select_for_update(of=("self",))
        return queryset.filter(token_hash=_hash(token)).first()

    @classmethod
    def detail(cls, user, token: str) -> dict:
        """Ce que voit la personne invitée avant d'accepter : l'entreprise et l'état de l'invitation."""
        invitation = cls._by_token(token)
        if invitation is None:
            raise NotFound("Invitation introuvable.")
        state = invitation_state(invitation)
        company = invitation.company
        return {
            "state": state,
            "message": STATE_MESSAGES.get(state, ""),
            "company": {"id": company.id, "name": company.name, "is_verified": company.is_verified},
            "already_in_company": MeService.get_entreprise_profil(user) is not None,
            "email_mismatch": bool(invitation.email) and invitation.email != user.email.lower(),
        }

    @classmethod
    @transaction.atomic
    def accept(cls, user, token: str) -> dict:
        """Accepte l'invitation : crée le profil entreprise (non propriétaire) et consomme le lien."""
        invitation = cls._by_token(token, for_update=True)
        if invitation is None:
            raise NotFound("Invitation introuvable.")
        state = invitation_state(invitation)
        if state != STATE_VALID:
            raise ValidationError({"error": STATE_MESSAGES[state], "state": state})
        if MeService.get_entreprise_profil(user) is not None:
            raise ValidationError({"error": "Vous êtes déjà rattaché à une entreprise : une seule entreprise par membre."})
        if invitation.email and invitation.email != user.email.lower():
            raise ValidationError({"error": "Cette invitation est destinée à une autre adresse e-mail."})

        MeService.create_entreprise_profil(user, invitation.company, is_owner=False)
        invitation.status = InvitationEntreprise.STATUS_ACCEPTED
        invitation.accepted_by = user
        invitation.accepted_at = timezone.now()
        invitation.save(update_fields=["status", "accepted_by", "accepted_at", "updated_at"])
        return {"company": {"id": invitation.company_id, "name": invitation.company.name}}
