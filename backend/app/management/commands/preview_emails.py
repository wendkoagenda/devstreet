"""Aperçu des e-mails transactionnels avec des données d'exemple, sans déclencher d'action réelle.

    python manage.py preview_emails                      # écrit les aperçus HTML et texte dans un dossier temporaire
    python manage.py preview_emails --out ./apercus      # ... dans le dossier donné
    python manage.py preview_emails --only welcome       # un seul e-mail
    python manage.py preview_emails --to moi@exemple.com # envoie aussi chaque e-mail à cette adresse (SMTP configuré)
"""
import tempfile
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email

from app.core.services import email_catalog as catalog
from app.core.services.email_service import EmailService, frontend_link

SAMPLE_TO = 'ada.lovelace@exemple.com'


def sample_specs():
    """Un exemple de chaque e-mail du catalogue, indexé par nom de gabarit."""
    specs = [
        catalog.welcome(SAMPLE_TO, 'Ada'),
        catalog.password_reset_code(SAMPLE_TO, 'Ada', '482913', 15),
        catalog.password_change_code(SAMPLE_TO, 'Ada', '730264', 15),
        catalog.password_changed(SAMPLE_TO, 'Ada'),
        catalog.provider_linked(SAMPLE_TO, 'Ada', 'github'),
        catalog.application_sent(SAMPLE_TO, 'Ada', 'Développeur·se React / Django', 'Kora Fintech'),
        catalog.application_received(
            SAMPLE_TO,
            'Moussa',
            'Ada Lovelace',
            'Développeuse full-stack, 6 ans d\'expérience',
            'Développeur·se React / Django',
            42,
            "Bonjour, votre projet de paiement mobile m'intéresse beaucoup : j'ai livré une API similaire l'an dernier.",
        ),
        catalog.application_accepted(SAMPLE_TO, 'Ada', 'Développeur·se React / Django', 'Kora Fintech'),
        catalog.application_rejected(SAMPLE_TO, 'Ada', 'Développeur·se React / Django', 'Kora Fintech'),
        catalog.network_match(SAMPLE_TO, 'Ada', 'Grace Hopper', 'Architecte cloud', 7),
        catalog.company_invitation(
            SAMPLE_TO, 'Moussa Traoré', 'Kora Fintech', frontend_link('/entreprise/invitation/exemple'), 7
        ),
    ]
    return {spec.template_name: spec for spec in specs}


class Command(BaseCommand):
    help = "Produit un aperçu de chaque e-mail transactionnel avec des données d'exemple (fichiers HTML/texte ou envoi de test)."

    def add_arguments(self, parser):
        parser.add_argument('--out', help="Dossier où écrire les aperçus (défaut : dossier temporaire)")
        parser.add_argument('--only', help="Nom d'un seul e-mail (ex. welcome, application_received)")
        parser.add_argument('--to', help="Adresse qui reçoit aussi chaque e-mail (envoi réel via la configuration SMTP)")

    def handle(self, *args, **options):
        specs = sample_specs()
        only = options.get('only')
        if only:
            if only not in specs:
                raise CommandError(f"E-mail inconnu : {only}. Choix possibles : {', '.join(sorted(specs))}")
            specs = {only: specs[only]}

        recipient = options.get('to')
        if recipient:
            try:
                validate_email(recipient)
            except ValidationError as exc:
                raise CommandError(f"Adresse e-mail invalide : {recipient}") from exc

        out_dir = Path(options.get('out') or Path(tempfile.gettempdir()) / 'devstreet-email-previews')
        out_dir.mkdir(parents=True, exist_ok=True)

        service = EmailService()
        for name, spec in specs.items():
            text_body, html_body = service.render(spec.template_name, spec.context)
            (out_dir / f'{name}.html').write_text(html_body, encoding='utf-8')
            (out_dir / f'{name}.txt').write_text(text_body, encoding='utf-8')
            if recipient:
                service.send_templated(recipient, f"[Aperçu] {spec.subject}", spec.template_name, spec.context)
            self.stdout.write(f"  {name} : {spec.subject}")

        self.stdout.write(self.style.SUCCESS(f"{len(specs)} aperçu(s) écrit(s) dans {out_dir}"))
        if recipient:
            self.stdout.write(self.style.SUCCESS(f"{len(specs)} e-mail(s) envoyé(s) à {recipient}"))
