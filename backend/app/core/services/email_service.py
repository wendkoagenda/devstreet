"""
Service d'envoi d'e-mails transactionnels (texte + HTML).

Deux modes :
- `send_templated` : envoi immédiat, l'appelant gère l'erreur (codes de confirmation : l'utilisateur ne peut pas
  continuer sans le code, l'échec doit lui être signalé).
- `queue_templated` / `queue` : envoi déclenché après la validation de la transaction en cours, dans un fil séparé.
  La réponse n'attend pas le serveur SMTP et un échec est seulement journalisé : il n'annule jamais l'action.
"""
import logging
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)

BRAND_NAME = 'DevStreet'


def mask_email(email: str) -> str:
    """Adresse masquée pour les journaux : « a***@exemple.com »."""
    local, _, domain = (email or '').partition('@')
    if not domain:
        return '***'
    return f"{local[:1]}***@{domain}"


def frontend_link(path: str) -> str:
    """Lien absolu vers une page de l'application (les e-mails n'ont pas de lien relatif)."""
    return f"{settings.FRONTEND_URL}/{path.lstrip('/')}"


@dataclass(frozen=True)
class EmailSpec:
    """Un e-mail prêt à partir : destinataire, objet, gabarit et variables (valeurs simples uniquement)."""

    to_email: str
    subject: str
    template_name: str
    context: Dict[str, Any] = field(default_factory=dict)


class EmailService:
    """
    Envoie des e-mails à partir de gabarits `core/emails/<nom>.txt` et `<nom>.html`.

    Le contexte peut contenir des données sensibles (code de vérification) :
    il n'est jamais journalisé, et l'adresse du destinataire est masquée dans les journaux.
    """

    TEMPLATE_DIR = 'core/emails'

    # ------------------------------------------------------------------ rendu
    def render(self, template_name: str, context: Dict[str, Any]) -> Tuple[str, str]:
        """Retourne (texte, html) du gabarit, avec les variables communes (marque, liens, année)."""
        full_context = {
            'brand_name': BRAND_NAME,
            'frontend_url': settings.FRONTEND_URL,
            'year': timezone.localdate().year,
            **context,
        }
        text_body = render_to_string(f'{self.TEMPLATE_DIR}/{template_name}.txt', full_context)
        html_body = render_to_string(f'{self.TEMPLATE_DIR}/{template_name}.html', full_context)
        return text_body, html_body

    # ------------------------------------------------------------------ envoi immédiat
    def send_templated(self, to_email: str, subject: str, template_name: str, context: Dict[str, Any]) -> None:
        """
        Envoie un e-mail construit à partir d'un gabarit, immédiatement.

        Raises:
            Exception: Toute erreur d'envoi ou de gabarit (à gérer par l'appelant)
        """
        text_body, html_body = self.render(template_name, context)
        message = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        message.attach_alternative(html_body, 'text/html')
        message.send(fail_silently=False)
        logger.info("E-mail « %s » envoyé à %s (gabarit %s)", subject, mask_email(to_email), template_name)

    def send(self, spec: EmailSpec) -> None:
        """Envoi immédiat d'un `EmailSpec` (l'appelant gère l'erreur)."""
        self.send_templated(spec.to_email, spec.subject, spec.template_name, spec.context)

    # ------------------------------------------------------------------ envoi différé
    def _send_safely(self, spec: EmailSpec) -> None:
        """Envoi qui ne lève jamais : un échec est journalisé (sans contenu ni adresse complète)."""
        try:
            self.send(spec)
        except Exception:  # noqa: BLE001 - un e-mail ne doit jamais faire échouer l'action qui l'a déclenché
            logger.exception(
                "Échec de l'envoi de l'e-mail (gabarit %s, destinataire %s)",
                spec.template_name,
                mask_email(spec.to_email),
            )

    def queue(self, spec: EmailSpec) -> None:
        """
        Programme l'envoi après la validation de la transaction en cours (rien n'est envoyé si elle est annulée).

        L'envoi a lieu dans un fil séparé, sauf si EMAIL_SEND_IN_THREAD vaut False (tests, commandes).
        """
        if not spec.to_email:
            return

        def start() -> None:
            if settings.EMAIL_SEND_IN_THREAD:
                threading.Thread(target=self._send_safely, args=(spec,), daemon=True).start()
            else:
                self._send_safely(spec)

        transaction.on_commit(start)

    def queue_templated(self, to_email: str, subject: str, template_name: str, context: Dict[str, Any]) -> None:
        """Raccourci de `queue` à partir des éléments de l'e-mail."""
        self.queue(EmailSpec(to_email, subject, template_name, context))
