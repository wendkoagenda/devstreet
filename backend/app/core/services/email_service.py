"""
Service d'envoi d'e-mails transactionnels (texte + HTML).
"""
import logging
from typing import Any, Dict
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


class EmailService:
    """
    Envoie des e-mails à partir de gabarits `core/emails/<nom>.txt` et `<nom>.html`.

    Le contexte peut contenir des données sensibles (code de réinitialisation) :
    il n'est jamais journalisé.
    """

    TEMPLATE_DIR = 'core/emails'

    def send_templated(self, to_email: str, subject: str, template_name: str, context: Dict[str, Any]) -> None:
        """
        Envoie un e-mail construit à partir d'un gabarit.

        Args:
            to_email (str): Adresse du destinataire
            subject (str): Objet du message
            template_name (str): Nom du gabarit sans extension (ex: "password_reset")
            context (Dict[str, Any]): Variables du gabarit

        Raises:
            Exception: Toute erreur d'envoi ou de gabarit (à gérer par l'appelant)
        """
        text_body = render_to_string(f'{self.TEMPLATE_DIR}/{template_name}.txt', context)
        html_body = render_to_string(f'{self.TEMPLATE_DIR}/{template_name}.html', context)

        message = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        message.attach_alternative(html_body, 'text/html')
        message.send(fail_silently=False)
        logger.info("E-mail '%s' envoyé (gabarit %s)", subject, template_name)
